import library
import unittest
import sys
import random


class SimpleTest(unittest.TestCase):
    def setUp(self):

        self.parser = library.Parser()
        self.parser.add_option('key', required=True,
                               type=int, unique_key="local")
        self.parser.add_option('name',  type=str, unique_key="local")
        self.parser.add_option('key2',  type=float)
        self.parser.add_option('name1', unique_key="remote", type=str)
        pass

    def test_print(self):
        self.commands = ['--key=123', '--key2=1234.6', '--name1=Shivam']
        self.assertEqual(self.parser.parse(self.commands),
                         {'key': 123,  'key2': 1234.6, 'name1': 'Shivam'})

    def test_required_args(self):
        self.commands = ['--key=123']
        self.assertEqual(self.parser.parse(self.commands), {'key': 123})
        self.commands = ['--key2=123.6']
        with self.assertRaisesRegex(library.ParserError, 'mandatoryerror'):
            self.parser.parse(self.commands)

    def test_unexpected_args(self):
        self.commands = ['--key=1234']
        self.assertEqual(self.parser.parse(self.commands), {'key': 1234})
        self.commands = ['--key3=123', '--key=123']
        with self.assertRaisesRegex(library.ParserError, "unexpected .*"):
            self.parser.parse(self.commands)

    def test_typeof_args(self):
        self.commands = ['--key=123.6']
        with self.assertRaisesRegex(library.ParserError, 'typeerror'):
            self.parser.parse(self.commands)
        self.commands = ['--key=1234s']
        with self.assertRaisesRegex(library.ParserError, 'typeerror'):
            self.parser.parse(self.commands)
        self.commands = ['--key=123gh', '--name1=Shiva12']
        with self.assertRaisesRegex(library.ParserError, 'typeerror'):
            self.parser.parse(self.commands)
        self.commands = ['--key=123', '--name1=Shivam', '--key2=123.78s']
        with self.assertRaisesRegex(library.ParserError, 'typeerror'):
            self.parser.parse(self.commands)

    def test_conflict(self):
        self.commands = ['--key=123', '--key2=1234.6', '--name1=Shivam']
        self.assertEqual(self.parser.parse(self.commands),
                         {'key': 123,  'key2': 1234.6, 'name1': 'Shivam'})
        self.commands = ['--key=123', '--name=Shiva']
        with self.assertRaisesRegex(library.ParserError, "conflict.*"):
            self.parser.parse(self.commands)


if __name__ == '__main__':
    unittest.main()
