import unittest
import sys
import os

# Add the path to the "scripts" directory to the sys.path
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(script_dir)

import convertV3  # noqa: E402

class TestProcessFile(unittest.TestCase):
    def test_process_file(self):
        # Read the input content from 'test.yml'
        with open('tests/test.yml', 'r') as input_file:
            input_content = input_file.read()

        # Create a temporary file with the input content
        with open('tests/temp_test_file.yml', 'w') as temp_file:
            temp_file.write(input_content)

        def load_fqcn_mapping():
          fqcn_mapping = {}
          with open('fqcn_mapping.txt', 'r') as file:
              for line in file:
                  parts = line.strip().split(':')
                  if len(parts) == 2:
                      module_name, fqcn_prefix = parts[0].strip(), parts[1].strip()
                      fqcn_mapping[module_name] = fqcn_prefix
          return fqcn_mapping
        fqcn_mapping = load_fqcn_mapping()
        # Call the process_file function on the temporary file
        convertV3.process_file('tests/temp_test_file.yml', fqcn_mapping)

        # Read the modified file's content
        with open('tests/temp_test_file.yml', 'r') as temp_file:
            modified_content = temp_file.read()

        # Read the expected result from 'test_result.txt'
        with open('tests/test_result.txt', 'r') as expected_file:
            expected_content = expected_file.read()

        # Set self.maxDiff to None to see the entire diff
        self.maxDiff = None

        # Assert that the modified content matches the expected result
        self.assertEqual(modified_content, expected_content)

        # Clean up the temporary file (optional)
        os.remove('tests/temp_test_file.yml')

if __name__ == '__main__':
    unittest.main()
