import unittest
import parser as parse

class UnitTesting(unittest.TestCase):
    parser = parse.Parser()
    def test_basic_usage(self):
        command_line_parameters = ['./test', '--key=1234', '--name=ayush']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, '{"--key": "1234", "--name": "ayush"}')

    def test_invalid_key(self):
        command_line_parameters = ['./test', '--key=ayush', '--name=ayush']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: The value for argument '--key' must be integer")

    def test_required_argument(self):
        command_line_parameters = ['./test', '--name=ayush']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error : argument '--key' is required but missing")

    def test_invalid_name(self):
        command_line_parameters = ['./test', '--key=1234', '--name=1234']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: The value for argument '--name' must be string")

    def test_no_arguments(self):
        command_line_parameters = ['./test']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: no arguments given in input")

    def test_local_and_remote(self):
        command_line_parameters = ['./test', '--local', '--remote']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: The '--local' and '--remote' arguments cannot be used together")

    def test_unrecognized_command(self):
        command_line_parameters = ['./test', '--roll']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: invalid argument '--roll'")

    def test_valueless_argument(self):
        command_line_parameters = ['./test', '--key']
        result = self.parser.main(command_line_parameters)
        self.assertEqual(result, "Error: The value for argument '--key' is missing")


if __name__ == '__main__':
    unittest.main()
