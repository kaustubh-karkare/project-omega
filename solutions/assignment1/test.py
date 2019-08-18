import library
import unittest
import sys


class simple_test(unittest.TestCase):
    def setUp(self):
        self.printer = library.parser()
        self.printer.add_options(key=(1234, "r", "local"))
        self.printer.add_options(name=("Shivam", "nr", "local"))
        self.commands = ['--key=123', '--name=s']
        self.test = self.printer.parsecommands(self.commands)
        pass

    def test_print(self):
        self.assertEqual(self.test, {'key': 123, 'name': 's'})

    def test_required_args(self):
        self.assertEqual(self.test, {'key': 123, 'name': 's'})

    def test_typeof_args(self):
        self.commands = ['--key=123.7', '--name=s']
        self.assertEqual(self.printer.parsecommands(
            self.commands), {'key': 123, 'name': 's'})


if __name__ == '__main__':
    unittest.main()
    """
    printer = library.parser()
    printer.add_options(key=(1234, "r", "local"))
    printer.add_options(name=("shivam", "nr", "local"))
    commands = ['--key=123', '--name=s']
    printer.parsecommands(commands)
    """
