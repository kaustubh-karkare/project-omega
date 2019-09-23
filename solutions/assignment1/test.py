import library
import unittest
import sys


class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.parser = library.Parser()
        self.parser.add_option('key', required=True,
                               type=int, unique_key="local")
        self.parser.add_option('name',  type=str, unique_key="remote")
        self.parser.add_option('key2', unique_key="local", type=float)
        self.parser.add_option('name1', unique_key="local", type=str)
        pass

    def test_print(self):
        self.commands = ['--key=123', '--key2=1234.6', '--name1=Shivam']
        self.assertEqual(self.parser.parse(self.commands),
                         {'key': 123,  'key2': 1234.6, 'name1': 'Shivam'})

    def test_required_args(self):
        self.commands = ['--key=123']
        self.assertEqual(self.parser.parse(self.commands), {'key': 123})
        self.commands = ['--key2=123.6']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'mandatoryerror')

    def test_overflow_args(self):
        self.commands = ['--key=1234']
        self.assertEqual(self.parser.parse(self.commands), {'key': 1234})
        self.commands = ['--key3=123', '--key=123']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'unexpected')

    def test_typeof_args(self):
        self.commands = ['--key=123.6']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'typeerror')
        self.commands = ['--key=1234s']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'typeerrorstring')
        self.commands = ['--key=123', '--name1=Shiva12']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'typeerrorstring')
        self.commands = ['--key=123', '--name1=Shivam', '--key2=123']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(str(error), 'typeerror')

    def test_conflict(self):
        self.commands = ['--key=123', '--key2=1234.6', '--name1=Shivam']
        self.assertEqual(self.parser.parse(self.commands),
                         {'key': 123,  'key2': 1234.6, 'name1': 'Shivam'})
        self.commands = ['--key=123', '--name=Shiva']
        try:
            self.parser.parse(self.commands)
        except Exception as error:
            self.assertEqual(error.value, 'conflict')


if __name__ == '__main__':
    unittest.main()
