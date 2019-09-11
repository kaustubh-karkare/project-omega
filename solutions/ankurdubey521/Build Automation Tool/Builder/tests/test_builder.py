import unittest
import subprocess
import os
import re
from Builder.main import execute


class TestBuilder(unittest.TestCase):

    def test_compilation_basic(self):
        path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        execute('run', path, os.getcwd() + '/test_builder_files/test_compilation_basic')
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
        execute('clean', path, os.getcwd())

    def test_commands_referenced_from_root(self):
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        execute('run', path, os.getcwd() + '/test_builder_files/test_commands_referenced_from_root')
        output_file_path = path + '/output'
        result = ''
        with open(output_file_path) as file_handle:
            result = file_handle.readable()
        execute('clean', path, os.getcwd() + '/test_builder_files/test_commands_referenced_from_root')
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()
