import unittest
import CommandLineParser as CLP


class TestCommandLParser(unittest.TestCase):

    def test_basic_usage(self): #all valid instructions here
        parser = CLP.CommandLineParser()
        parser.add_command('--key', format = r'\d+')
        parser.add_command('--name', format = r'[a-zA-Z]+', required_command = '--key')
        parser.add_command('--local', conflicting_command = '--remote', is_flag = True)
        parser.add_command('--remote', conflicting_command = '--local', is_flag = True)

        command_line_param = ['./test', '--key=123', '--name=pranjal'] #key and name
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--key": "123", "--name": "pranjal"}')


        command_line_param = ['./test', '--local'] #test local
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--local": true}')


        command_line_param = ['./test', '--remote'] #test remote
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '{"--remote": true}')



    def test_invalid_usage(self): #all invalid instructions here
        parser = CLP.CommandLineParser()
        parser.add_command('--key', format = r'\d+')
        parser.add_command('--name', format = r'[a-zA-Z]+', required_command = '--key')
        parser.add_command('--local', conflicting_command = '--remote', is_flag = True)
        parser.add_command('--remote', conflicting_command = '--local', is_flag = True)

        command_line_param = ['./test', '--key=1a3', '--name=pranjal'] #invalid key
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
            self.assertEqual(str(result), 'The --remote and --local arguments cannot be used together')
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