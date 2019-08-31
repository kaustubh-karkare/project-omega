import unittest
import parser as myparser
import json

class TestParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = myparser.Parser()
    
    def test_required_arguments_not_present_raises_error(self):
        self.parser.add_option('--key','key','positive integer', required=True)
        self.parser.add_option('--name','name','string', required=False)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test','--name=kanjal'])
        self.assertEqual(error.exception.message,"Missing Required Argument --key")

    def test_value_to_key_not_a_positive_integer_raises_error(self):
        self.parser.add_option('--key','key','positive integer', required=True)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test','--key=cat'])
        self.assertEqual(error.exception.message,"Expected type positive integer but got str in command --key")
    
    def test_mutually_exclusive_commands_present_raises_error(self):
        self.parser.add_option('--key', 'key', 'positive integer', required=True)
        self.parser.add_option('--name', 'name', 'string', required=True)
        self.parser.add_option('--local', 'local', 'string', required=False)
        self.parser.add_option('--remote', 'remote', 'string', required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'])
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--key=123', '--name=kanjal', '--local', '--remote'])
        self.assertEqual(error.exception.message,"The commands --local --remote cannot be used together")

    def test_unknown_command_raises_error(self):
        self.parser.add_option('--key', 'key', 'positive integer', required=False)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--name=kanjal'])
        self.assertEqual(error.exception.message, "Unknown Command --name")
   
    def test_parsing_key_name(self): 
        self.parser.add_option('--key', 'key', 'positive integer', required=True)
        self.parser.add_option('--name', 'name', 'string', required=True)
        self.parser.add_option('--local', 'local', 'string', required=False)
        self.parser.add_option('--remote', 'remote', 'string', required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'])
        parsed_json = self.parser.parse(['./test', '--key=123', '--name=kanjal'])
        self.assertEqual(json.loads(parsed_json), {'--key':'123', '--name':'kanjal'})

    def test_parsing_key_name_remote(self):
        self.parser.add_option('--key', 'key', 'positive integer', required=True)
        self.parser.add_option('--name', 'name', 'string', required=True)
        self.parser.add_option('--local', 'local', 'string', required=False)
        self.parser.add_option('--remote', 'remote', 'string', required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'])
        parsed_json = self.parser.parse(['./test', '--key=123', '--name=kanjal', '--remote'])
        self.assertEqual(json.loads(parsed_json), {'--key':'123', '--name':'kanjal', '--remote':'True'})


if __name__ == '__main__':
    unittest.main()
