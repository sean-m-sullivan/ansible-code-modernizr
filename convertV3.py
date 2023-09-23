import os
import re
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

def load_fqcn_mapping(mapping_file):
  fqcn_mapping = {}
  try:
    with open(mapping_file, 'r') as file:
      for line in file:
        parts = line.strip().split(':')
        if len(parts) == 2:
          module_name, fqcn_prefix = parts[0].strip(), parts[1].strip()
          fqcn_mapping[module_name] = fqcn_prefix
  except FileNotFoundError:
    logging.error(f"Mapping file '{mapping_file}' not found.")
  return fqcn_mapping

def process_file(file_path, fqcn_mapping):
  try:
    with open(file_path, 'r') as file:
      file_contents = file.read()

    patterns_and_replacements = [
      # Jinja spacing
      (r'{{?([\w|(])', lambda match: "{{ " + match.group(1)),
      (r'(\w|\))}}', lambda match: match.group(1) + " }}"),
      (r'(\w)\|(\w)', lambda match: match.group(1) + " |"),
      # TODO fix (r'(\w)\|(\w)', lambda match: "| " + match.group(2)),
      # Adds space after #'s
      (r'#(\w)', lambda match: "# " + match.group(1)),
      # Caps first character after - name:
      (r'(- name:\s)(\w)', lambda match:  match.group(1) + (match.group(2)).capitalize()),
      # Removes double blank lines
      (r'\n\s*\n', '\n\n'),
    ]

    # Apply each pattern and replacement function
    for pattern, replacement_function in patterns_and_replacements:
      file_contents = re.sub(pattern, replacement_function, file_contents)

    # Replace module names with their corresponding FQCN prefixes
    for module_name, fqcn_prefix in fqcn_mapping.items():
      pattern = fr'\s({re.escape(module_name)}:)'
      replacement = f' {fqcn_prefix}.\g<1>' # noqa W605 #TODO come back and look into this
      file_contents = re.sub(pattern, replacement, file_contents)

    # Check if '---' is present at the start of the file, if not, add it
    if not file_contents.startswith('---\n'):
      file_contents = '---\n' + file_contents

    # Check if '...' is present at the end of the file, if not, add it
    if not file_contents.endswith('\n...\n'):
      file_contents = file_contents.rstrip() + '\n...\n'

    # Open the file for writing with the modified contents
    with open(file_path, 'w') as file:
      file.write(file_contents)

    logging.info(f"Processed file: {file_path}")
  except Exception as e:
    logging.error(f"Error processing file {file_path}: {str(e)}")


def process_files_in_parallel(directory_path, skip_list, skip_dirs, fqcn_mapping):
  with ThreadPoolExecutor() as executor:
    for root, dirs, files in os.walk(directory_path):
      # Filter out directories based on the provided skip_dirs argument
      dirs[:] = [d for d in dirs if d not in skip_dirs]
      for file_name in files:
        if file_name in skip_list:
          continue
        elif file_name.endswith(('.yml', '.yaml')):
          file_path = os.path.join(root, file_name)
          executor.submit(process_file, file_path, fqcn_mapping)

def main():
  parser = argparse.ArgumentParser(description="YAML file processing script")
  parser.add_argument('--path', required=True, help="Directory path to search for YAML files")
  parser.add_argument('--skip-dirs', nargs='*', default=['.github'], help="List of directories to skip")
  parser.add_argument('--skip-list', nargs='*', default=['requirements.yml'], help="List of files to skip")
  parser.add_argument('--mapping-file', required=True, help="File containing module name to FQCN mappings")

  args = parser.parse_args()

  # Configure logging
  logging.basicConfig(filename='yaml_processing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

  # Load FQCN mapping from the specified file
  fqcn_mapping = load_fqcn_mapping(args.mapping_file)

  if not fqcn_mapping:
    logging.error("No valid mapping found. Exiting.")
    return

  # Process files in parallel
  process_files_in_parallel(args.path, args.skip_list, args.skip_dirs, fqcn_mapping)

if __name__ == "__main__":
  main()
