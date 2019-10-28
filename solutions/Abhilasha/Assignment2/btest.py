import unittest

import os

from os import path

import BuildAutomationTool as BAT


class TestBuildAutomationTool(unittest.TestCase):
    
    
	def test_build_test_all(self):

		BAT_obj = BAT.Action()

		BAT_obj.get_command(os.getcwd(), 'build', 'test_all')

		self.assertEqual(path.exists('test.o'), True)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_bubble.o'), True)

		self.assertEqual(path.exists('sort_quick.o'), True)

		self.assertEqual(path.exists('sort_merge.o'), True)

		os.chdir(cwd)
        
    
	def test_build_clean(self):

		BAT_obj = BAT.Action()

		BAT_obj.get_command(os.getcwd(), 'build', 'clean')

		self.assertEqual(path.exists('test.o'), False)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_bubble.o'), False)

		self.assertEqual(path.exists('sort_quick.o'), False)

		self.assertEqual(path.exists('sort_merge.o'), False)

		os.chdir(cwd)
        
        
	def test_build_test_sort_bubble(self):

		BAT_obj = BAT.Action()

		BAT_obj.get_command(os.getcwd(), 'build', 'test_sort_bubble')

		self.assertEqual(path.exists('test.o'), True)

		cwd = os.getcwd()

		os.chdir(cwd+"\\algorithms")

		self.assertEqual(path.exists('sort_bubble.o'), True)

		os.chdir(cwd)
        
        
	def test_invalid_command(self):

		BAT_obj = BAT.Action()
        
		with self.assertRaisesRegex(Exception, 'Command not recognized.'):

			BAT_obj.get_command(os.getcwd(), 'build', 'test_sort_selection')
    

if __name__ == '__main__':

	unittest.main()
    