import unittest
import subprocess
import os
from Builder.main import Builder


class TestBuilder(unittest.TestCase):
    # TODO: Implement running tests from /tmp/

    # The tests should work for any path inside the project
    def setUp(self):
        while os.path.basename(os.getcwd()) != 'Build Automation Tool':
            os.chdir('..')
        os.chdir('Builder/tests')

    def test_basic_shell_command(self):
        command = "echo 'Hello World!'"
        exit_code = Builder().run_shell(command, cwd='/')
        self.assertEqual(0, exit_code)

    def test_nonzero_exit_code_for_shell_command(self):
        command = "exit 1"
        exit_code = Builder().run_shell(command, cwd='/')
        self.assertEqual(1, exit_code)

    def test_compilation_basic(self):
        builder = Builder()
        path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        builder.execute_build_rule('run', path, path)
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
        builder.execute_build_rule('clean', path, os.getcwd())
        self.assertFalse(os.path.isfile(path + "/test.out"))

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
        # Perhaps there is a better method of doing this ?
        builder._root_dir_abs = path
        builder._build_rule_handler('run', path, dry_run=True)
        output_file_path = path + '/output'
        self.assertFalse(os.path.isfile(output_file_path))

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
