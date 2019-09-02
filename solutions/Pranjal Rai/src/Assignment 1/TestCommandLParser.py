import unittest
from CommandLineParser import CommandLineParser


class TestCommandLParser(unittest.TestCase):
    def test_basic_usage(self):
        command_line_param = ['./test', '--key=123', '--name=pranjal']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, '{"--key": "123", "--name": "pranjal"}')

    def test_invalid_key(self):
        command_line_param = ['./test', '--key=1a3', '--name=pranjal']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, 'invalid argument to --key')

    def test_invalid_name(self):
        command_line_param = ['./test', '--key=123', '--name=pranjal123']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, 'invalid argument to --name')

    def test_missing_key(self):
        command_line_param = ['./test', '--name=pranjal']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, 'The --key argument is required, but missing from input')

    def test_local(self):
        command_line_param = ['./test', '--local']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, '{"--local": true}')

    def test_remote(self):
        command_line_param = ['./test', '--remote']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, '{"--remote": true}')

    def test_remote_with_local(self):
        command_line_param = ['./test', '--remote', '--local']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, 'The --local and --remote arguments cannot be used together')

    def test_unrecognized_command(self):
        command_line_param = ['./test', '--version']
        result = CommandLineParser().get_arguments(command_line_param)
        self.assertEqual(result, '--version is not a recognized command')


if __name__ == '__main__':
    unittest.main()
