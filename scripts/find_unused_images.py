## Make sure you set the ROOT and ASSETS correctly while running the script
import os
import fnmatch

ROOT='./openg2p-documentation'
ASSETS = os.path.join(ROOT, '.gitbook/assets')

def list_files(directory):
    file_names = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_names.append(file_path)
    return file_names

def grep_text(directory, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.md'):
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r') as file:
                    for line_number, line in enumerate(file, start=1):
                        if pattern in line:
                            match = f"{file_path}:{line_number}: {line.strip()}"
                            matches.append(match)
            except UnicodeDecodeError:
                pass # Skip files that can't be decoded as text (e.g., binary files)
    return matches


all_assets = list_files(ASSETS)
for asset in all_assets:
    asset = os.path.basename(asset).strip()
    results = grep_text(ROOT, asset)
    if len(results) == 0:
        print(f'Not found: {asset}')



