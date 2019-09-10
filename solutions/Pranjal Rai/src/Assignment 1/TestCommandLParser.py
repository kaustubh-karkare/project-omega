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
        with self.assertRaisesRegexp(Exception, 'invalid argument to --key'):
            parser.get_arguments(command_line_param)

        command_line_param = ['./test', '--key=123', '--name=pranjal123'] #invalid name
        with self.assertRaisesRegexp(Exception, 'invalid argument to --name'):
            parser.get_arguments(command_line_param)


        command_line_param = ['./test', '--name=pranjal'] #missing key
        with self.assertRaisesRegexp(Exception, 'The --key argument is required, but missing from input'):
            parser.get_arguments(command_line_param)


        command_line_param = ['./test', '--remote', '--local'] #local and remote together
        with self.assertRaisesRegexp(Exception, 'The --remote and --local arguments cannot be used together'):
            parser.get_arguments(command_line_param)


        command_line_param = ['./test', '--version'] #unrecognized command
        with self.assertRaisesRegexp(Exception, '--version is not a recognized command'):
            parser.get_arguments(command_line_param)


if __name__ == '__main__':
    unittest.main()