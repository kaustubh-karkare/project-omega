import unittest
import parser as parse

class UnitTesting(unittest.TestCase):
    parser = parse.Parser()
    
    def test_basic_usage(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        command_line_parameters = ['./test', '--key=1234', '--name=ayush']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, '{"--key": "1234", "--name": "ayush"}')

    def test_invalid_key(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--key=ayush', '--name=ayush'])
        self.assertEqual("Error: The value for argument '--key' must be integer", str(error.exception))

    def test_required_argument(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--name=ayush'])
        self.assertEqual("Error : argument '--key' is required but missing", str(error.exception))

    def test_invalid_name(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--key=1234', '--name=1234'])
        self.assertEqual("Error: The value for argument '--name' must be string", str(error.exception))

    def test_no_arguments(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test'])
        self.assertEqual("Error: no arguments given in input", str(error.exception))

    def test_local_and_remote(self):
        self.parser.add_argument('--local', False, 'others')
        self.parser.add_argument('--remote', False, 'others')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--local', '--remote'])
        self.assertEqual("Error: The '--local' and '--remote' arguments cannot be used together", str(error.exception))

    def test_unrecognized_command(self):
        self.parser.add_argument('--key', True, 'integer')
        self.parser.add_argument('--name', False, 'string')
        self.parser.add_argument('--local', False, 'others')
        self.parser.add_argument('--remote', False, 'others')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--roll'])
        self.assertEqual("Error: invalid argument '--roll'", str(error.exception))

    def test_valueless_argument(self):
        self.parser.add_argument('--key', True, 'integer')
        with self.assertRaises(parse.ParseError) as error:
            self.parser.main(['./test', '--key'])
        self.assertEqual("Error: The value for argument '--key' is missing", str(error.exception))

if __name__ == '__main__':
    unittest.main()
