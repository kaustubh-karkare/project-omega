import unittest
import CommandLineParser as CLP


class TestCommandLParser(unittest.TestCase):

    def test_basic_usage(self): #all valid instructions here
        parser = CLP.CommandLineParser()
        parser.add_command('--key', format = r'\d+', is_required = True)
        parser.add_command('--name', format = r'[a-zA-Z]+')
        parser.add_command('--local', conflicting_command = '--remote', is_flag = True)
        parser.add_command('--remote', conflicting_command = '--local', is_flag = True)

        command_line_param = ['./test', '--key=123', '--name=pranjal'] #key and name
        result = parser.get_arguments(command_line_param)['final_response']
        self.assertEqual(result, '{"--key": "123", "--name": "pranjal"}')


        command_line_param = ['./test', '--local'] #test local
        result = parser.get_arguments(command_line_param)['final_response']
        self.assertEqual(result, '{"--local": true}')


        command_line_param = ['./test', '--remote'] #test remote
        result = parser.get_arguments(command_line_param)['final_response']
        self.assertEqual(result, '{"--remote": true}')



    def test_invalid_usage(self): #all invalid instructions here
        parser = CLP.CommandLineParser()
        parser.add_command('--key', format = r'\d+', is_required = True)
        parser.add_command('--name', format = r'[a-zA-Z]+')
        parser.add_command('--local', conflicting_command = '--remote', is_flag = True)
        parser.add_command('--remote', conflicting_command = '--local', is_flag = True)

        command_line_param = ['./test', '--key=1a3', '--name=pranjal'] #invalid key
        result = parser.get_arguments(command_line_param)
        self.assertRaises(result, 'invalid argument to --key')


        command_line_param = ['./test', '--key=123', '--name=pranjal123'] #invalid name
        result = parser.get_arguments(command_line_param)
        self.assertRaises(result, 'invalid argument to --name')


        command_line_param = ['./test', '--name=pranjal'] #missing key
        result = parser.get_arguments(command_line_param)
        self.assertRaises(result, 'The --key argument is required, but missing from input')
        

        command_line_param = ['./test', '--remote', '--local'] #local and remote together
        result = parser.get_arguments(command_line_param)
        self.assertRaises(result, 'The --remote and --local arguments cannot be used together')


        command_line_param = ['./test', '--version'] #unrecognized command
        result = parser.get_arguments(command_line_param)
        self.assertEqual(result, '--version is not a recognized command')


if __name__ == '__main__':
    unittest.main()