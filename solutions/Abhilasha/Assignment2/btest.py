import unittest
import os
from os import path
import BuildAutomationTool as BAT


class TestBuildAutomationTool(unittest.TestCase):
    
    
	def test_build_test_all(self):

		BAT_obj = BAT.Action()

		BAT_obj.get_command(os.getcwd(), 'build', 'test_all')

		self.assertEqual(path.exists('test.o'), True)
        
		self.assertEqual(path.exists('test_sort_bubble.exe'), True)

		self.assertEqual(path.exists('test_sort_quick.exe'), True)

		self.assertEqual(path.exists('test_sort_merge.exe'), True)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_bubble.o'), True)

		self.assertEqual(path.exists('sort_quick.o'), True)

		self.assertEqual(path.exists('sort_merge.o'), True)

		os.chdir(cwd)
    
        
	def test_clean(self):
        
        
		BAT_obj = BAT.Action()

		BAT_obj.get_command(os.getcwd(), 'build', 'clean')
        
		self.assertEqual(path.exists('test.o'), False)
        
		self.assertEqual(path.exists('test_sort_bubble.exe'), False)

		self.assertEqual(path.exists('test_sort_quick.exe'), False)

		self.assertEqual(path.exists('test_sort_merge.exe'), False)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_bubble.o'), False)

		self.assertEqual(path.exists('sort_quick.o'), False)

		self.assertEqual(path.exists('sort_merge.o'), False)

		os.chdir(cwd)
        
        
	def test_sort_merge(self):
        
		BAT_obj2 = BAT.Action()

		BAT_obj2.get_command(os.getcwd(), 'build', 'test_sort_merge')
        
		self.assertEqual(path.exists('test.o'), True)
        
		self.assertEqual(path.exists('test_sort_merge.exe'), True)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_merge.o'), True)

		os.chdir(cwd)
        
        
	def test_invalid_key(self):

		BAT_obj = BAT.Action()
        
		with self.assertRaisesRegex(Exception, 'Command not recognized.'):
            
			BAT_obj.get_command(os.getcwd(), 'build', 'test_sort_selection')


if __name__ == '__main__':

	unittest.main()
    