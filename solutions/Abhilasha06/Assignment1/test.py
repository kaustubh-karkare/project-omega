"""
@author: Abhilasha
"""
import unittest
from my_parser import MyParser
class Tests(unittest.TestCase):
    """
    some test cases
    """
    MyParser.add_option('--key', 'int', 'True')
    MyParser.add_option('--name', 'str', 'True')
    MyParser.add_option('--local', 'str', 'False')
    MyParser.add_option('--remote', 'str', 'False')
    def test_only_key_defined(self):
        ans = MyParser.check_argument("./test --key=123")
        self.assertEqual('{"--key": "123"}', ans)
    def test_key_and_name_defined(self):
        ans = MyParser.check_argument("./test --key=12345 --name=kaustubh")
        self.assertEqual('{"--key": "12345", "--name": "kaustubh"}', ans)
    def test_invalid_key(self):
        ans = MyParser.check_argument("./test --key=cat")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         +' but missing or has invalid value.', ans)
    def test_no_key(self):
        ans = MyParser.check_argument("./test --local --remote")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         ' but missing or has invalid value.', ans)
    def test_no_key_with_local_and_name(self):
        ans = MyParser.check_argument("./test --local --name=abcd")
        self.assertEqual('Error: The \'--key\' argument is required,'
                         ' but missing or has invalid value.', ans)
    def test_undefined_field(self):
        ans = MyParser.check_argument("./test --age=19")
        self.assertEqual('Error: Field not defined', ans)
    def test_local_remote_together(self):
        ans = MyParser.check_argument("./test --key=19 --local --remote")
        self.assertEqual('Error: --local and --remote can\'t occur together', ans)
    def test_key_and_local_defined(self):
        ans = MyParser.check_argument("./test --key=19 --local")
        self.assertEqual('{"--key": "19", "--local": "true"}', ans)
if __name__ == '__main__':
    unittest.main()
    