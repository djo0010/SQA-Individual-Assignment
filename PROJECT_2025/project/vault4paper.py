from http import client
from itertools import count
from venv import create
import hvac 
import random 

import re
from pathlib import Path

import string

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

counter_mapper           = {}
hvac_token               = "hvs.dkWvyEIwTSxgA5ey3dIUCtqW" ## this should come from the output of *vault server -dev* 
hvac_url                 = "http://127.0.0.1:8200"        ## this should come from the output of *vault server -dev*
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
    print("Finished storing secrets!")
    print('='*50)    


def retrieveSecrets( tech_str ): 
    clientObj = makeConn() 
    for counter, v_ in counter_mapper.items():
        retrieveSecret( clientObj,  counter, tech_str )
    print('='*50)


SUSPICIOUS_KEYWORDS = {
    "password", "secret", "token", "key", "uuid", "encryption",
    "hmac", "cookie", "hash", "api", "auth", "client_secret",
    "db_password", "private_key"
}


def is_probably_secret(key, value):
    """
    Strong heuristic to determine if a key-value pair is likely a secret.
    This avoids false positives from config values or trivial strings.
    """

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
    if len(value) < 6:  # Too short to be a realistic secret
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

def is_start_of_rsa_key_block(line):
    """
    Returns True if the line looks like the start of a multi-line RSA private key block.
    """
    if bool(re.search(r'^\s*-{5}BEGIN RSA PRIVATE KEY-{5}\s*$', line.strip())) or bool(re.search(r'^\s*-{5}BEGIN PRIVATE KEY-{5}\s*$', line.strip())):
        return True
    return False
    


def handle_multiline_rsa_secret(lines, start_index, hvac_token, hvac_url):

    key_line = lines[start_index].strip()

    block = []  # Start block with the first line
    i = start_index + 1
    while i < len(lines):
        line = lines[i].rstrip()
        block.append(line)
        if line.strip() == "-----END RSA PRIVATE KEY-----":
            break
        i += 1

    # Join the lines to preserve formatting
    full_rsa_key = '\n'.join(block)

    print(f"Full RSA Key Block:\n{full_rsa_key}")

    # Store the RSA key in Vault
    secret_path = f'SECRET_PATH_{random.randint(1, 100000)}'
    client = makeConn()
    client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret={'password': full_rsa_key})

    # Create the lookup placeholder for the YAML
    placeholder_line = key_line.split(":")[0] + f': |'  # Keep the '|' in the YAML
    placeholder_line += f"\n  {{{{ lookup(\'hashi_vault\', \'secret={secret_path} token={hvac_token} url={hvac_url}\')[\'password\'] }}}}'"

    # Return the new placeholder, the original block, and line numbers for logging
    return placeholder_line, block, start_index, i - 1


def scan_yml_secrets_and_replace(directory, log_file_path="replaced_secrets_log.txt"):
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
                    i = 0
                    while i < len(lines):
                        line = lines[i]

                        if i + 1 < len(lines) and is_start_of_rsa_key_block(lines[i + 1]):
                            placeholder_line, block, start_line_num, end_line_num = handle_multiline_rsa_secret(
                                lines, i, hvac_token, hvac_url
                            )
                            new_lines.append(placeholder_line)

                            print(placeholder_line)

                            # Log RSA block replacement
                            log_file.write(f"File: {file_path}, Lines: {start_line_num + 1}-{end_line_num + 1}\n")
                            log_file.write("Original:\n" + ''.join(block))
                            log_file.write("\n")
                            log_file.write(f"Replaced: {placeholder_line.strip()}\n")
                            log_file.write("-" * 60 + "\n")

                            i = end_line_num + 2
                            continue  # ✅ Skip rest of loop for RSA block

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

                        if is_probably_secret(key, value):
                            secret_path = storeSecret(makeConn(), value, random.randint(1, 100000))
                            placeholder = f'{{{{ lookup(\'hashi_vault\', \'secret={secret_path} token={hvac_token} url={hvac_url}\') }}}}'

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
                        else:
                            new_lines.append(line)

                        i += 1

                    # Write the modified content back to the YAML file
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.writelines(new_lines)

                except Exception as e:
                    print(f"Could not read or write {file_path}: {e}")

    print(f"Finished scanning and updating YAML files. Log saved to '{log_file_path}'")
    return secrets_found


# Scan for secrets
results = scan_yml_secrets_and_replace("C:/Users/djoak/OneDrive/Documents/SQA-2025/SQA-Individual-Assignment/PROJECT_2025/project/Ansible")




