import BuildAutomationTool as Build
import argparse
import os

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Command Line Parser for Build Automation Tool')
	parser.add_argument("command", help = "indication to build processes")
	parser.add_argument("build_command", help = "different build commands")
	args = parser.parse_args()
	build_automation_tool_object = Build.BuildAutomationTool()
	build_automation_tool_object.execute_command(os.getcwd(), os.getcwd(), args.command, args.build_command)