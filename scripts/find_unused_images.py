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


def filter_files(assets, extensions):
   """
   assets: list of filenames
   extentions: list of extensions. Example, ['.txt', '.drawio', '.TXT']
   Remove all the files with extensions mentioned in the list 'extensions'. The search is case sensitive
   so make sure you give all the extensions.
   """
   filtered = []
   extensions = [x.strip() for x in extensions]
   for asset in assets:
      _, extension = os.path.splitext(asset) 
      if extension.strip() not in extensions: 
          filtered.append(asset)
   return filtered
 
       
all_assets = list_files(ASSETS)
filtered_assets = filter_files(all_assets, ['.drawio'])
# Create a shell script file to delete the unwanted files
delete_file = 'delete-files.sh'
df = open(delete_file, 'wt')
df.write('#!/bin/sh\n')
for asset in filtered_assets:
    full_path = asset
    asset = os.path.basename(asset).strip()
    results = grep_text(ROOT, asset)
    if len(results) == 0:
        print(f'Not found: {asset}')
        df.write(f'rm -f "{full_path}"\n')
print(f'Created {delete_file}. Run `sh {delete_file}` on command prompt')
df.close()


