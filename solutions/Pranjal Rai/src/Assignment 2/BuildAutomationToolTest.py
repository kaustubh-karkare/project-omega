import unittest
import BuildAutomationTool as Build
import os
from os import path


class TestBuildAutomationTool(unittest.TestCase):

	def test_build_clean(self):
		build_automation_tool_object = Build.BuildAutomationTool()
		build_automation_tool_object.execute_command(os.getcwd(), os.getcwd(), 'build', 'clean')
		current_location = os.getcwd()
		absolute_location = os.path.abspath(current_location)
		os.chdir(absolute_location)
		self.assertEqual(path.exists('test.o'), False)
		previous_location = absolute_location
		absolute_location += "/algorithms"
		os.chdir(absolute_location)
		self.assertEqual(path.exists('sort_bubble.o'), False)
		self.assertEqual(path.exists('sort_quick.o'), False)
		self.assertEqual(path.exists('sort_merge.o'), False)
		os.chdir(previous_location)
		

	def test_build_run(self):
		build_automation_tool_object = Build.BuildAutomationTool()
		build_automation_tool_object.execute_command(os.getcwd(), os.getcwd(), 'build', 'run')
		current_location = os.getcwd()
		absolute_location = os.path.abspath(current_location)
		os.chdir(absolute_location)
		self.assertEqual(path.exists('test.o'), True)
		previous_location = absolute_location
		absolute_location += "/algorithms"
		os.chdir(absolute_location)
		self.assertEqual(path.exists('sort_bubble.o'), True)
		self.assertEqual(path.exists('sort_quick.o'), True)
		self.assertEqual(path.exists('sort_merge.o'), True)
		os.chdir(previous_location)


	def test_invalid_usage(self):
		build_automation_tool_object = Build.BuildAutomationTool()
		with self.assertRaisesRegexp(Exception, 'unknown_process_command is not a recognized process command'):
			build_automation_tool_object.execute_command(os.getcwd(), os.getcwd(), 'unknown_process_command', 'clean')

		with self.assertRaisesRegexp(Exception, 'build unknown_command is not a recognized command'):
			build_automation_tool_object.execute_command(os.getcwd(), os.getcwd(), 'build', 'unknown_command')




if __name__ == '__main__':
	unittest.main()