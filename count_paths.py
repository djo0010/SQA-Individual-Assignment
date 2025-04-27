#!/usr/bin/env python3

import os
import re
import sys

def count_secret_paths_and_tokens_in_directory(input_dir, output_file):
    secret_path_pattern = re.compile(r'SECRET_PATH_(\d+)')
    token_pattern = re.compile(r'token=(hvs\.[\w\d]+)')
    secret_counts = {}
    token_counts = {}

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(('.yml', '.yaml', '.txt', '.pp')):  # add more extensions if needed
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                        # Count SECRET_PATH_xxxxx
                        secrets = secret_path_pattern.findall(content)
                        for s in secrets:
                            secret_counts[s] = secret_counts.get(s, 0) + 1

                        # Count token=hvs.XXXXX
                        tokens = token_pattern.findall(content)
                        for t in tokens:
                            token_counts[t] = token_counts.get(t, 0) + 1

                except Exception as e:
                    print(f"⚠️ Warning: Could not read {file_path}: {e}")

    # Write results
    with open(output_file, 'w') as f:
        f.write("=== SECRET_PATH Counts ===\n")
        for key, value in sorted(secret_counts.items()):
            f.write(f"{key}: {value}\n")

        f.write("\n=== Vault Token Counts ===\n")
        for key, value in sorted(token_counts.items()):
            f.write(f"{key}: {value}\n")

    print(f"✅ Done! Found {len(secret_counts)} unique SECRET_PATHs and {len(token_counts)} unique tokens. Output written to '{output_file}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_file.txt>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    count_secret_paths_and_tokens_in_directory(input_dir, output_file)
