import unittest
import subprocess
import os
from Builder.main import Builder


class TestBuilder(unittest.TestCase):

    def test_compilation_basic(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        builder.execute_build_rule('run', path, path)
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
        builder.execute_build_rule('clean', path, os.getcwd())

    def test_commands_referenced_from_root(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        builder.execute_build_rule('run', path, path)
        output_file_path = path + '/output'
        result = ''
        with open(output_file_path) as file_handle:
            result = file_handle.readable()
        builder.execute_build_rule('clean', path, os.getcwd() + '/test_builder_files/test_commands_referenced_from_root')
        self.assertEqual(True, result)

    def test_dry_run_does_not_write_files(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        builder._build_rule_handler('run', path, path, dry_run=True)
        output_file_path = path + '/output'
        self.assertEqual(False, os.path.isfile(output_file_path))

    def test_basic_circular_dependency_throws_exception(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency_throws_exception'
        self.assertRaises(Builder.CircularDependencyException, builder.execute_build_rule, 'A', path, path)

    def test_basic_circular_dependency2_throws_exception(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency2_throws_exception'
        self.assertRaises(Builder.CircularDependencyException, builder.execute_build_rule, 'A', path, path)


if __name__ == '__main__':
    unittest.main()
