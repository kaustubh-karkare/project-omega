"""
@author: Abhilasha
"""
import unittest
from my_parser import MyParser
class Tests(unittest.TestCase):
    """
    some test cases
    """
    
    def setUp(self):
        self.Parser=MyParser()
      
        
    def test_only_key_defined(self):
        self.Parser.add_option('--key', dtype='int', nargs=2)
        ans = self.Parser.check_argument(['./test', '--key=123'])
        self.assertEqual({'--key': '123'}, ans)
             
        
    def test_key_and_name_defined(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2)
        self.Parser.add_option('--name', dtype='str', nargs = 2)
        ans = self.Parser.check_argument(['./test', '--key=12345', '--name=kaustubh'])
        self.assertEqual({'--key': '12345', '--name': 'kaustubh'}, ans)
        
        
    def test_invalid_key(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2)
        with self.assertRaises(Exception) as context:
            self.Parser.check_argument(['./test', '--key=cat'])
        self.assertEqual('The field has invalid value.', str(context.exception))
        
        
    def test_local_remote(self):
        self.Parser.add_option('--local', dtype='str', nargs = 1)
        with self.assertRaises(Exception) as context:
            self.Parser.check_argument(['./test', '--local', '--remote'])
        self.assertEqual("Invalid field given.", str(context.exception))
        
        
    def test_local_and_name(self):
        self.Parser.add_option('--name', dtype='str', nargs = 2)
        self.Parser.add_option('--local', dtype='str', nargs = 1)
        ans = self.Parser.check_argument(['./test', '--local', '--name=abcd'])
        self.assertEqual({'--local': 'True', '--name': 'abcd'}, ans)
        
        
    def test_undefined_field(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2) 
        with self.assertRaises(Exception) as context:
            self.Parser.check_argument(['./test', '--age=19'])
        self.assertEqual('Invalid field given.', str(context.exception))

        
    def test_extra_field_given(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2)
        self.Parser.add_option('--local', dtype='str', nargs = 1)
        with self.assertRaises(Exception) as context:
            self.Parser.check_argument(['./test', '--key=19', '--local', '--remote'])
        self.assertEqual('Invalid field given.', str(context.exception))
        
        
    def test_key_and_local_defined(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2)
        self.Parser.add_option('--local', dtype='str', nargs = 1)
        ans = self.Parser.check_argument(['./test', '--key=19', '--local'])
        self.assertEqual({'--key': '19', '--local': 'True'}, ans)
      
        
    def test_no_arguments(self):
        self.Parser.add_option('--key', dtype='int', nargs = 2)
        with self.assertRaises(Exception) as context:
            self.Parser.check_argument(['./test'])
        self.assertEqual('No arguments.', str(context.exception))
      
        
    def test_age(self):
        self.Parser.add_option('--age', dtype='int', nargs=2)
        ans = self.Parser.check_argument(['./test', '--age=19'])
        self.assertEqual({'--age': '19'}, ans)
        
if __name__ == '__main__':
    unittest.main()
    