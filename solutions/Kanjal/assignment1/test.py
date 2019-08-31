import unittest
import parser as myparser
import json

class TestParser(unittest.TestCase):

    def setUp(self):
        self.parser = myparser.Parser()

    def test_required_arguments_not_present_raises_error(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=False)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--name=kanjal'])
        self.assertEqual(error.exception.message, "Missing Required Argument --key")

    def test_value_to_key_not_a_positive_integer_raises_error(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--key=cat'])
        self.assertEqual(error.exception.message, "Expected type positive integer"\
			" but got str in command --key")

    def test_mutually_exclusive_commands_present_raises_error(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=True)
        self.parser.add_option('--local', 'local', myparser.OptionType.STRING, required=False)
        self.parser.add_option('--remote', 'remote', myparser.OptionType.STRING, required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'], is_one_required=False)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--key=123', '--name=kanjal', '--local', '--remote'])
        self.assertEqual(error.exception.message, "The commands --local --remote "\
			"cannot be used together")

    def test_unknown_command_raises_error(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=False)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--name=kanjal'])
        self.assertEqual(error.exception.message, "Unknown Command --name")

    def test_parsing_key_name(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=True)
        parsed_json = self.parser.parse(['./test', '--key=123', '--name=kanjal'])
        self.assertEqual(json.loads(parsed_json), {'--key':'123', '--name':'kanjal'})

    def test_parsing_key_name_remote(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=True)
        self.parser.add_option('--local', 'local', myparser.OptionType.STRING, required=False)
        self.parser.add_option('--remote', 'remote', myparser.OptionType.STRING, required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'], is_one_required=False)
        parsed_json = self.parser.parse(['./test', '--key=123', '--name=kanjal', '--remote'])
        self.assertEqual(json.loads(parsed_json), {'--key':'123', '--name':'kanjal',
			'--remote':'True'})

    def test_invalid_type_of_option_description(self):
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.add_option('--key', bool, 'positive integer', required=True)
        self.assertEqual(error.exception.message, "Option Type Should be an instance of OptionType"\
			" Enum,currently OptionType.STRING OptionType.POSITIVEINTEGER are supported")

    def test_atleast_one_from_exclusive_options_required_but_missing_raises_error(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=True)
        self.parser.add_option('--local', 'local', myparser.OptionType.STRING, required=False)
        self.parser.add_option('--remote', 'remote', myparser.OptionType.STRING, required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'], is_one_required=True)
        with self.assertRaises(myparser.ValidationError) as error:
            self.parser.parse(['./test', '--key=123', '--name=kanjal'])
        self.assertEqual(error.exception.message, "Atleast one from the mutually exclusive options"\
			" --local --remote required")

    def test_parsing_key_name_when_one_from_exclusive_options_not_required(self):
        self.parser.add_option('--key', 'key', myparser.OptionType.POSITIVEINTEGER, required=True)
        self.parser.add_option('--name', 'name', myparser.OptionType.STRING, required=True)
        self.parser.add_option('--local', 'local', myparser.OptionType.STRING, required=False)
        self.parser.add_option('--remote', 'remote', myparser.OptionType.STRING, required=False)
        self.parser.add_mutually_exclusive_options(['--local', '--remote'], is_one_required=False)
        parsed_json = self.parser.parse(['./test', '--key=123', '--name=kanjal'])
        self.assertEqual(json.loads(parsed_json), {'--key':'123', '--name':'kanjal'})

if __name__ == '__main__':
    unittest.main()
