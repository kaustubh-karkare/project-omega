import unittest
class Tests(unittest.TestCase):
    def setUp(self):
        self.st=cli()
        
    def test_simple0(self):
       
        a=self.st.check_argument("./test --key=123")
        self.assertEqual( '{"--key": "123"}',a)
        
    def test_simple1(self):
       
        a=self.st.check_argument("./test --key=12345 --name=kaustubh")
        self.assertEqual( '{"--key": "12345", "--name": "kaustubh"}',a)
      
    def test_simple2(self):
       
        a=self.st.check_argument("./test --key=cat")
        self.assertEqual( 'Error: The value for the \'--key\' argument must be a positive integer.',a)
       
    def test_simple3(self):
       
        a=self.st.check_argument("./test --local --remote")
        self.assertEqual( 'Error: --local and --remote can\'t occur together',a)
        
    def test_simple4(self):
       
        a=self.st.check_argument("./test --local --name=abcd")
        self.assertEqual( 'Error: The \'--key\' argument is required, but missing from input.',a)
        
        
    if( __name__=='__main__'):
        unittest.main()