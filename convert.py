import os
import re

skip_dirs_list = ['.github']
skip_list = ['requirements.yml']
# Define the directory path where you want to search for .yml and .yaml files
directory_path = './testing/'

# Define multiple patterns and their corresponding replacement functions
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
  # FQCN fix
  (r'\s(add_host:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(apt:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(apt_key:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(apt_repository:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(assemble:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(assert:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(async_status:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(blockinfile:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(command:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(copy:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(cron:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(deb822_repository:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(debconf:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(debug:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(dnf:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(dnf5:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(dpkg_selections:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(expect:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(fail:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(fetch:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(file:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(find:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(gather_facts:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(get_url:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(getent:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(git:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(group:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(group_by:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(hostname:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(import_playbook:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(import_role:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(import_tasks:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(include:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(include_role:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(include_tasks:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(include_vars:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(iptables:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(known_hosts:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(lineinfile:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(meta:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(package:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(package_facts:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(pause:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(ping:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(pip:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(raw:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(reboot:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(replace:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(rpm_key:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(script:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(service:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(service_facts:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(set_fact:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(set_stats:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(setup:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(shell:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(slurp:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(stat:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(subversion:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(systemd_service:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(sysvinit:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(tempfile:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(template:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(unarchive:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(uri:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(user:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(validate_argument_spec:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(wait_for:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(wait_for_connection:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(yum:)', lambda match: ' ansible.builtin.' + match.group(1)),
  (r'\s(yum_repository:)', lambda match: ' ansible.builtin.' + match.group(1)),
]

# Recursively search for .yml and .yaml files in the directory and its subdirectories
for root, dirs, files in os.walk(directory_path):
  # Filter out directories that contain any of the skip_dirs_list
  dirs[:] = [d for d in dirs if not any(keyword in d for keyword in skip_dirs_list)]
  for file_name in files:
    if file_name in skip_list:
      continue
    elif file_name.endswith(('.yml', '.yaml')):
      file_path = os.path.join(root, file_name)

      # Open the file for reading
      with open(file_path, 'r') as file:
        file_contents = file.read()

      # Apply each pattern and replacement function
      for pattern, replacement_function in patterns_and_replacements:
        file_contents = re.sub(pattern, replacement_function, file_contents)

      # Check if '---' is present at the start of the file, if not, add it
      if not file_contents.startswith('---\n'):
        file_contents = '---\n' + file_contents

      # Check if '...' is present at the end of the file, if not, add it
      if not file_contents.endswith('\n...\n'):
        file_contents = file_contents.rstrip() + '\n...\n'

      # Open the file for writing with the modified contents
      with open(file_path, 'w') as file:
        file.write(file_contents)
