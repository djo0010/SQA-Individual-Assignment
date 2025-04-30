from http import client
from itertools import count
from venv import create
import hvac 
import random 

import re
from pathlib import Path

import string

from dotenv import load_dotenv
import os

'''

1. Install Vault 

- `brew tap hashicorp/tap` 

- `brew install hashicorp/tap/vault` 

2. Verify the HCP Vault installation: 
- `vault` 


3. Start the HCP Vault server. This will help us to programmatically store secrets 
- `vault server -dev` 

4. Keep an eye on the output of `vault server -dev` . From the output we will use `address` and `token` 
5. `pip install hvac`

'''

load_dotenv(dotenv_path=".env")
hvac_token = os.getenv("HVAC_TOKEN")
hvac_url   = os.getenv("HVAC_URL")

counter_mapper           = {}
ansible_secret_retrieval = '"{{ lookup(' + "'hashi_vault', 'secret=secret/data/"  
puppet_secret_retrieval  = "Deferred('vault_lookup::lookup', ["  

def makeConn():
    hvc_client = hvac.Client(url= hvac_url, token= hvac_token) 
    return hvc_client 

def storeSecret( client,  secr1 , cnt  ):
    secret_path     = 'SECRET_PATH_' + str( cnt  )
    create_response = client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=dict(password =  secr1 ) )
    # print( type( create_response ) )
    # print( dir( create_response)  )

def retrieveSecret(client_, cnt_, tech_str): 
    secret_path        = 'SECRET_PATH_' + str( cnt_  )
    read_response      = client_.secrets.kv.read_secret_version(path=secret_path, raise_on_deleted_version=False) 
    secret_from_vault  = read_response['data']['data']['password']
    # print('The secret we have obtained:')
    print()
    print("To retrieve the secret '{}' please plugin the following code snippet in your script:".format( secret_from_vault) )

    if tech_str == 'A': 
        # print(secret_path)
        # print(ansible_secret_retrieval)
        print(ansible_secret_retrieval + secret_path + " token=" + hvac_token + " url=" + hvac_url + "')['password'] }}" + '"') # change-01

    elif tech_str == 'P':
        # print(puppet_secret_retrieval + '"' + secret_path + '/' + hvac_token  + '", ' + hvac_url + "']),"  )
        print(puppet_secret_retrieval + '"' + secret_path + '/' + hvac_token  + '", \'' + hvac_url + "']),"  ) # change-02


def preprocessTechInput(tech_str):
    str2ret = ''
    tech_str = tech_str.replace('\n', '')
    tech_str = tech_str.replace('\r', '')    
    str2ret  = tech_str 
    return str2ret

def storeSecrets(lis_secr, tech_str): 
    clientObj    =  makeConn() 
    for secret2store in lis_secr: 
        counter = random.randint(1, 100000)
        storeSecret( clientObj,   secret2store, counter )
        counter_mapper[counter] = tech_str


def retrieveSecrets( tech_str ): 
    clientObj = makeConn() 
    for counter, v_ in counter_mapper.items():
        retrieveSecret( clientObj,  counter, tech_str )
    print('='*50)


def is_probably_secret_yml(key, value):
    SUSPICIOUS_KEYWORDS = {
        "password", "secret", "token", "key", "uuid", "encryption",
        "hmac", "cookie", "hash", "api", "auth", "client_secret",
        "db_password", "private_key"
    }

    key = key.strip().lower().strip('"\'')
    value = value.strip().strip('"\'')
    
    # Skip empty values
    if not value:
        return False
    if value == "secret" or value == "NA":
        return True
    # Skip obvious non-secrets
    if value.isdigit():
        return False
    if value in {"true", "false", "null", "~"}:
        return False
    if all(c in string.punctuation for c in value):  # Just symbols
        return False
    if key.startswith("#") or key.startswith("//"):
        return False

    # Suspicious keys
    if any(keyword in key for keyword in SUSPICIOUS_KEYWORDS):
        return True

    # Encoded or random-looking values (base64, tokens, hashes)
    if re.fullmatch(r'[A-Za-z0-9+/]{20,}={0,2}', value):  # base64-like
        return True
    if re.fullmatch(r'[A-Fa-f0-9]{32,}', value):  # hex tokens, hashes
        return True

    # Environment variable placeholders, ignore them
    if re.match(r'^\$\{?[A-Z0-9_]+\}?$', value):
        return False

    return False

def is_probably_secret_puppet(key, value):
    key = key.strip().lower().strip('"\'')
    value = value.strip().strip('"\'')
    
    IGNORED_KEYWORDS = {
        "user", "username", "tenant", "type", "email", "dbname", "host",
        "public_url", "admin_url", "auth_type", "project_name", "project_domain_name",
        "user_domain_name", "endpoint", "uri", "class", "keystone_tenant", "keystone_user"
    }
    SENSITIVE_FRAGMENTS = {"password", "secret", "token", "private", "key", "auth", "connection", "uuid"}


    if any(kw in key for kw in SENSITIVE_FRAGMENTS) and key not in IGNORED_KEYWORDS:
        return True
    if any(kw in key for kw in IGNORED_KEYWORDS):
        return False

    if not value or value.lower() in {"true", "false", "null", "~"}:
        return False
    if value.isdigit() and len(value) < 4:
        return False
    if all(c in string.punctuation for c in value):
        return False
    if re.match(r'^\$\{?[A-Z0-9_]+\}?$', value):
        return False

    if re.fullmatch(r'[A-Za-z0-9+/]{20,}={0,2}', value):  # base64
        return True
    if re.fullmatch(r'[A-Fa-f0-9]{32,}', value):  # hex
        return True

    if "://" in value and re.search(r":[^@:]+@", value):  # username:password@ in URI
        return True

    if len(value) < 6 and any(kw in key for kw in SENSITIVE_FRAGMENTS):
        return True

    return False

def is_start_of_rsa_key_block(line):
    if bool(re.search(r'^\s*-{5}BEGIN RSA PRIVATE KEY-{5}\s*$', line.strip())) or bool(re.search(r'^\s*-{5}BEGIN PRIVATE KEY-{5}\s*$', line.strip())):
        return True
    return False

def handle_multiline_rsa_secret(lines, start_index, hvac_token, hvac_url):
    key_line = lines[start_index].strip()

    # Extract full RSA private key block
    block = []
    i = start_index + 1
    while i < len(lines):
        line = lines[i].rstrip()
        block.append(line)
        if line.strip() == "-----END RSA PRIVATE KEY-----":
            break
        i += 1

    full_rsa_key = '\n'.join(block)

    # Store the secret using your storeSecrets function
    processed_secret = preprocessTechInput(full_rsa_key)
    storeSecrets([processed_secret], "A")  # This also updates counter_mapper

    # Use the last stored counter to generate the Vault lookup
    last_counter = list(counter_mapper.keys())[-1]
    secret_path = f'SECRET_PATH_{last_counter}'

    lookup_placeholder = (
        f"{{{{ lookup('hashi_vault', 'secret=secret/data/{secret_path} "
        f"token={hvac_token} url={hvac_url}')['password'] }}}}"
    )

    # YAML-compatible replacement line
    yaml_key = key_line.split(":")[0]
    placeholder_line = f"{yaml_key}: |\n  {lookup_placeholder}"

    # Return the new placeholder, the original block, and line numbers for logging
    return placeholder_line, block, start_index, i - 1

def scan_puppet_secrets_and_replace(directory, log_file_path="replaced_puppet_secrets_log.txt"):
    secrets_found = []
    print(f"Scanning Puppet directory: {directory}")

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("Puppet Replaced Secrets Log\n")
        log_file.write("=" * 60 + "\n")

        for file_path in Path(directory).rglob("*.pp"):
            print(f"Reading file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                new_lines = []
                local_secret_count = 0

                for i, line in enumerate(lines):
                    if "=>" not in line:
                        new_lines.append(line)
                        continue

                    try:
                        key_part, value_part = line.split("=>", 1)
                        key = key_part.strip()
                        value = value_part.strip().rstrip(',').strip('"\'')
                    except Exception as e:
                        print(f"Skipping line {i + 1} in {file_path} due to error: {e}")
                        new_lines.append(line)
                        continue

                    if is_probably_secret_puppet(key, value):
                        processed_secret = preprocessTechInput(value)
                        storeSecrets([processed_secret], "P")
                        last_counter = list(counter_mapper.keys())[-1]
                        secret_path = f'SECRET_PATH_{last_counter}'

                        vault_lookup = (
                            f"Deferred('vault_lookup::lookup', ['{secret_path}/{hvac_token}', '{hvac_url}']),"
                        )

                        # Calculate base indentation (based on the original line)
                        indent_match = re.match(r'^(\s*)', line)
                        indent = indent_match.group(1) if indent_match else '  '

                        # Generate well-formatted secret replacement
                        new_line = f"{indent}{key} => {vault_lookup}\n"


                        log_file.write(f"File: {file_path}, Line: {i + 1}\n")
                        log_file.write(f"Original: {line.strip()}\n")
                        log_file.write(f"Replaced: {new_line.strip()}\n")
                        log_file.write("-" * 60 + "\n")

                        secrets_found.append({
                            "file": str(file_path),
                            "line": i + 1,
                            "original_content": line.strip(),
                            "replaced_with": new_line.strip()
                        })
                        new_lines.append(new_line)
                        local_secret_count += 1
                    else:
                        new_lines.append(line)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(new_lines)

                print(f"Replaced {local_secret_count} secret(s) in file: {file_path}")

            except Exception as e:
                print(f"Could not read or write {file_path}: {e}")

    print(f"Finished scanning Puppet files. Log saved to '{log_file_path}'")
    return secrets_found

def scan_yml_secrets_and_replace(directory, log_file_path="replaced_yml_secrets_log.txt"):
    secrets_found = []
    print(f"Scanning directory: {directory}")

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("Replaced Secrets Log\n")
        log_file.write("=" * 60 + "\n")

        for ext in ("*.yml", "*.yaml"):
            for file_path in Path(directory).rglob(ext):
                print(f"Reading file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()

                    new_lines = []
                    local_secret_count = 0                    
                    i = 0
                    while i < len(lines):
                        line = lines[i]

                        if i + 1 < len(lines) and is_start_of_rsa_key_block(lines[i + 1]):
                            placeholder_line, block, start_line_num, end_line_num = handle_multiline_rsa_secret(
                                lines, i, hvac_token, hvac_url
                            )
                            new_lines.append(placeholder_line)

                            # Log RSA block replacement
                            log_file.write(f"File: {file_path}, Lines: {start_line_num + 1}-{end_line_num + 1}\n")
                            log_file.write("Original:\n" + ''.join(block))
                            log_file.write("\n")
                            log_file.write(f"Replaced: {placeholder_line.strip()}\n")
                            log_file.write("-" * 60 + "\n")

                            i = end_line_num + 2
                            local_secret_count += 1                            
                            continue

                        if ":" not in line:
                            new_lines.append(line)
                            i += 1
                            continue

                        try:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                        except Exception as e:
                            print(f"Skipping line {i + 1} in {file_path} due to error: {e}")
                            new_lines.append(line)
                            i += 1
                            continue

                        if is_probably_secret_yml(key, value):
                            processed_secret = preprocessTechInput(value)
                            storeSecrets([processed_secret], "A")
                            last_counter = list(counter_mapper.keys())[-1]
                            secret_path = f'SECRET_PATH_{last_counter}'
                            placeholder = (
                                f"{{{{ lookup('hashi_vault', 'secret=secret/data/{secret_path} "
                                f"token={hvac_token} url={hvac_url}')['password'] }}}}"
                            )

                            index = line.rfind(value)
                            if index != -1:
                                new_line = line[:index] + f'"{placeholder}"' + line[index + len(value):]
                            else:
                                new_line = line

                            # Log it
                            log_file.write(f"File: {file_path}, Line: {i + 1}\n")
                            log_file.write(f"Original: {line.strip()}\n")
                            log_file.write(f"Replaced: {new_line.strip()}\n")
                            log_file.write("-" * 60 + "\n")

                            secrets_found.append({
                                "file": str(file_path),
                                "line": i + 1,
                                "original_content": line.strip(),
                                "replaced_with": new_line.strip()
                            })
                            new_lines.append(new_line)
                            local_secret_count += 1                            
                        else:
                            new_lines.append(line)

                        i += 1

                    # Write the modified content back to the YAML file
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.writelines(new_lines)

                    print(f"Replaced {local_secret_count} secret(s) in file: {file_path}")

                except Exception as e:
                    print(f"Could not read or write {file_path}: {e}")

    print(f"Finished scanning and updating YAML files. Log saved to '{log_file_path}'")
    return secrets_found

def scan_puppet_secrets_only(directory):
    print(f"Scanning Puppet directory (read-only): {directory}")
    secrets_found = []

    for file_path in Path(directory).rglob("*.pp"):
        print(f"\n[FILE] {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if "=>" not in line:
                    continue

                try:
                    key_part, value_part = line.split("=>", 1)
                    key = key_part.strip()
                    value = value_part.strip().rstrip(',').strip('"\'')
                except Exception as e:
                    print(f"  Skipping line {i + 1} due to error: {e}")
                    continue

                if is_probably_secret_puppet(key, value):
                    print(f"  [Line {i + 1}] Potential secret → {key} => {value}")
                    secrets_found.append((file_path, i + 1, key, value))
        except Exception as e:
            print(f"Could not read {file_path}: {e}")

    print(f"\nCompleted scanning Puppet files. {len(secrets_found)} potential secrets found.")
    return secrets_found

def scan_yml_secrets_only(directory):
    print(f"Scanning YAML directory (read-only): {directory}")
    secrets_found = []

    for ext in ("*.yml", "*.yaml"):
        for file_path in Path(directory).rglob(ext):
            print(f"\n[FILE] {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                i = 0
                while i < len(lines):
                    line = lines[i]

                    if i + 1 < len(lines) and is_start_of_rsa_key_block(lines[i + 1]):
                        print(f"  [Line {i + 1}] Detected start of RSA key block.")
                        i += 1
                        continue

                    if ":" not in line:
                        i += 1
                        continue

                    try:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                    except Exception as e:
                        print(f"  Skipping line {i + 1} due to error: {e}")
                        i += 1
                        continue

                    if is_probably_secret_yml(key, value):
                        print(f"  [Line {i + 1}] Potential secret → {key}: {value}")
                        secrets_found.append((file_path, i + 1, key, value))

                    i += 1
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    print(f"\nCompleted scanning YAML files. {len(secrets_found)} potential secrets found.")
    return secrets_found

def runRegularVersion():
    print("Welcome!")
    print("This Python program will ask for inputs from you in order to store secrets and provide code to retrieve secrets.")
    print("First let's understand what technology are you using? Type 'A' for Ansible and 'P' for Puppet:")
    technology_string = input()
    preprocessTechInput( technology_string )
    print("Thanks. Please provide the secrets that you want this program to securely store:")
    inp_secret_holder = []
    while True: 
        print("Please provide the secret that you want the program to secure. Hit 'q' to quit:")
        secret = input() 
        secret = preprocessTechInput(secret)
        if secret == 'Q' or secret == 'q': 
            break
        inp_secret_holder.append( secret  )

    storeSecrets( inp_secret_holder, technology_string )
    print("Do you want the code snippet to retrieve your secrets? 'Y' for yes and 'N' for no.")

    retrieve = input()
    retrieve = preprocessTechInput( retrieve )
    if retrieve == 'Y' or retrieve == 'y': 
        retrieveSecrets( technology_string )
    elif retrieve == 'N' or retrieve == 'n': 
        print("Thanks for using the program. Goodbye Project!")

def list_all_secret_paths(hvac_client, mount_point="secret"):
    try:
        paths = hvac_client.secrets.kv.v2.list_secrets(path="", mount_point=mount_point)
        keys = paths.get("data", {}).get("keys", [])
        print(f"\nSecrets stored under mount '{mount_point}':")
        for key in keys:
            print(f"- {mount_point}/data/{key}")
        print("Total secrets in vault:",len(keys))
    except hvac.exceptions.InvalidPath:
        print(f"No secrets found or invalid path under mount '{mount_point}'")
    except Exception as e:
        print(f"Error retrieving secret paths: {e}")

def get_secret_by_path(hvac_client, secret_path, mount_point="secret"):
    try:
        response = hvac_client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point=mount_point,
            raise_on_deleted_version=False
        )
        data = response["data"]["data"]
        print(f"\nSecret at path '{mount_point}/{secret_path}':")
        for k, v in data.items():
            print(f"  {k}: {v}")
    except hvac.exceptions.InvalidPath:
        print(f"Secret not found at path: '{mount_point}/{secret_path}'")
    except Exception as e:
        print(f"Error retrieving secret: {e}")


if __name__ == "__main__":
    print("Please select an option:")
    print("1: Run interactive secret storage tool")
    print("2: Scan and replace secrets in YML and Puppet files")
    print("3: Only scan for secrets (no file replacement)")
    print("4: Retrieve all secrets")
    print("5: Retrieve details for a single entry")

    user_choice = input("Enter option number (1/2/3/4/5): ").strip()

    if user_choice == "1":
        runRegularVersion()
    elif user_choice == "2":
        resultsAnsible = scan_yml_secrets_and_replace("C:/Users/DJ/Documents/SQA_Project/SQA-2025/PROJECT_2025/project/Ansible")
        resultsPuppet = scan_puppet_secrets_and_replace("C:/Users/DJ/Documents/SQA_Project/SQA-2025/PROJECT_2025/project/Puppet")
    elif user_choice == "3":
        resultsAnsible = scan_yml_secrets_only("C:/Users/DJ/Documents/SQA_Project/SQA-2025/PROJECT_2025/project/Ansible")
        resultsPuppet = scan_puppet_secrets_only("C:/Users/DJ/Documents/SQA_Project/SQA-2025/PROJECT_2025/project/Puppet")
    elif user_choice == "4":
        client = makeConn()
        list_all_secret_paths(client)
    elif user_choice == "5":
        client = makeConn()
        list_all_secret_paths(client)
        chosen = input("Enter a secret path to retrieve (or press Enter to skip): ").strip()
        if chosen:
            get_secret_by_path(client, chosen)
    else:
        print("Invalid input. Please enter 1, 2, 3, 4, or 5.")


