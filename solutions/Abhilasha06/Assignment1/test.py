"""
@author: Abhilasha
"""
import unittest
from my_parser import MyParser, MyParserError
class Tests(unittest.TestCase):
    """
    some test cases
    """
    
    def setUp(self):
        self.parser = MyParser()
      
        
    def test_one_option_defined(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        ans = self.parser.check_options(['./test', '--key=123'])
        self.assertEqual({'--key': '123'}, ans)
             
        
    def test_two_options_defined(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        self.parser.add_option('--name', dtype='str', is_flag=True)
        ans = self.parser.check_options(['./test', '--key=12345', '--name=kaustubh'])
        self.assertEqual({'--key': '12345', '--name': 'kaustubh'}, ans)
        
        
    def test_three_options_defined(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        self.parser.add_option('--local', dtype='str', is_flag=False)
        self.parser.add_option('--remote', dtype='str', is_flag=False)
        ans = self.parser.check_options(['./test', '--key=19', '--local', '--remote'])
        self.assertEqual({'--key': '19', '--local': 'True', '--remote': 'True'}, ans)
        
        
    def test_option_with_invalid_datatype(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        with self.assertRaises(MyParserError) as context:
            self.parser.check_options(['./test', '--key=cat'])
        self.assertEqual('The field has invalid value.', str(context.exception))
        
        
    def test_unexpexted_option(self):
        self.parser.add_option('--local', dtype='str', is_flag=False)
        with self.assertRaises(MyParserError) as context:
            self.parser.check_options(['./test', '--local', '--remote'])
        self.assertEqual("Unexpected field given.", str(context.exception))
        
                
    def test_too_less_arguments_given(self):
        self.parser.add_option('--age', dtype='int', is_flag=True) 
        with self.assertRaises(MyParserError) as context:
            self.parser.check_options(['./test', '--age'])
        self.assertEqual('Too less arguments.', str(context.exception))

        
    def test_too_many_arguments_given(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        self.parser.add_option('--local', dtype='str', is_flag=False)
        with self.assertRaises(MyParserError) as context:
            self.parser.check_options(['./test', '--key=19', '--local=abc'])
        self.assertEqual('Too many arguments.', str(context.exception))
        
        
    def test_no_options_defined(self):
        self.parser.add_option('--key', dtype='int', is_flag=True)
        with self.assertRaises(MyParserError) as context:
            self.parser.check_options(['./test'])
        self.assertEqual('No options given.', str(context.exception))
      
               
if __name__ == '__main__':
    unittest.main()
    