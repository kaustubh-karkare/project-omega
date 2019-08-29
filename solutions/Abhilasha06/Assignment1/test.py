"""
@author: Abhilasha
"""
import unittest
from my_parser import MyParser
class Tests(unittest.TestCase):
    """
    some test cases
    """
    def test_simple0(self):
        """
        only key defined
        """
        ans = MyParser.check_argument("./test --key=123")
        self.assertEqual('{"--key": "123"}', ans)
    def test_simple1(self):
        """
        key and name defined
        """
        ans = MyParser.check_argument("./test --key=12345 --name=kaustubh")
        self.assertEqual('{"--key": "12345", "--name": "kaustubh"}', ans)
    def test_simple2(self):
        """
        key defined but has invalid value
        """
        ans = MyParser.check_argument("./test --key=cat")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         +' but missing or has invalid value.', ans)
    def test_simple3(self):
        """
        no key present
        """
        ans = MyParser.check_argument("./test --local --remote")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         ' but missing or has invalid value.', ans)
    def test_simple4(self):
        """
        no key present
        """
        ans = MyParser.check_argument("./test --local --name=abcd")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         ' but missing or has invalid value.', ans)
    def test_simple5(self):
        """
        undefined field
        """
        ans = MyParser.check_argument("./test --age=19")
        self.assertEqual('Error: Field not defined', ans)
    def test_simple6(self):
        """
        local and remote specified together
        """
        ans = MyParser.check_argument("./test --key=19 --local --remote")
        self.assertEqual('Error: --local and --remote can\'t occur together', ans)
    def test_simple7(self):
        """
        key and local defined
        """
        ans = MyParser.check_argument("./test --key=19 --local")
        self.assertEqual('{"--key": "19", "--local": "true"}', ans)
if __name__ == '__main__':
    unittest.main()
    