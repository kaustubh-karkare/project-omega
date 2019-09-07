import unittest
from CommandLineParser import CommandLineParser, AddCommand


class TestCommandLParser(unittest.TestCase):

    def test_basic_usage(self):
        commands = {}
        new_command = AddCommand
        new_command('--key', 'positive integer', r'\d+', None, None, False, commands)
        new_command('--name', 'albhapets only', r'[a-zA-Z]+', '--key', None, False, commands)
        new_command('--local', None, r'/\A\z/', None, '--remote', True, commands)
        new_command('--remote', None, r'/\A\z/', None, '--local', True, commands)
        parser = CommandLineParser(commands)

        command_line_param = ['./test', '--key=123', '--name=pranjal'] #key and name
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--key": "123", "--name": "pranjal"}')


        command_line_param = ['./test', '--local'] #test local
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--local": true}')


        command_line_param = ['./test', '--remote'] #test remote
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--remote": true}')



    def test_invalid_usage(self):
        command_line_param = ['./test', '--key=1a3', '--name=pranjal'] #invalid key
        commands = {}
        new_command = AddCommand
        new_command('--key', 'positive integer', r'\d+', None, None, False, commands)
        new_command('--name', 'albhapets only', r'[a-zA-Z]+', '--key', None, False, commands)
        new_command('--local', None, r'/\A\z/', None, '--remote', True, commands)
        new_command('--remote', None, r'/\A\z/', None, '--local', True, commands)
        parser = CommandLineParser(commands)
        try:
            result = parser.get_arguments(command_line_param)
            self.assertEqual(str(result), 'invalid argument to --key')
        except Exception as exception:
            print(exception)


        command_line_param = ['./test', '--key=123', '--name=pranjal123'] #invalid name
        try:
            result = parser.get_arguments(command_line_param)
            self.assertEqual(str(result), 'invalid argument to --name')
        except Exception as exception:
            print(exception)


        command_line_param = ['./test', '--name=pranjal'] #missing key
        try:
            result = parser.get_arguments(command_line_param)
            self.assertEqual(str(result), 'The --key argument is required, but missing from input')
        except Exception as exception:
            print(exception)


        command_line_param = ['./test', '--remote', '--local'] #local and remote together
        try:
            result = parser.get_arguments(command_line_param)
            self.assertEqual(str(result), 'The --local and --remote arguments cannot be used together')
        except Exception as exception:
            print(exception)


        command_line_param = ['./test', '--version'] #unrecognized command
        try:
            result = parser.get_arguments(command_line_param)
            self.assertEqual(str(result), '--version is not a recognized command')
        except Exception as exception:
            print(exception)



if __name__ == '__main__':
    unittest.main()