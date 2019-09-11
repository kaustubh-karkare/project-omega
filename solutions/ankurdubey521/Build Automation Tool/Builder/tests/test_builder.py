import unittest
import subprocess
import os
from Builder.main import execute, CircularDependencyException


class TestBuilder(unittest.TestCase):

    def test_compilation_basic(self):
        path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        execute('run', path, path)
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
        execute('clean', path, os.getcwd())

    def test_commands_referenced_from_root(self):
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        execute('run', path, path)
        output_file_path = path + '/output'
        result = ''
        with open(output_file_path) as file_handle:
            result = file_handle.readable()
        execute('clean', path, os.getcwd() + '/test_builder_files/test_commands_referenced_from_root')
        self.assertEqual(True, result)

    def test_dry_run_does_not_write_files(self):
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        execute('run', path, path, dry_run=True)
        output_file_path = path + '/output'
        self.assertEqual(False, os.path.isfile(output_file_path))

    def test_basic_circular_dependency_throws_exception(self):
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency_throws_exception'
        self.assertRaises(CircularDependencyException, execute, 'A', path, path, dry_run=True)

    def test_basic_circular_dependency2_throws_exception(self):
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency2_throws_exception'
        self.assertRaises(CircularDependencyException, execute, 'A', path, path, dry_run=True)


if __name__ == '__main__':
    unittest.main()
