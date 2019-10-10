import os
import sys
import json


class BuildAutomationTool():

	def execute_command(self, current_working_directory, previous_working_directory, current_script):
		absolute_path = os.path.abspath(current_working_directory)
		os.chdir(absolute_path)

		with open(os.path.join("build.json")) as json_file:
			scripts = json.load(json_file)
			script_found = False

			for script in scripts:
				if script['name'] == current_script:
					script_found = True
					if 'deps' in script:
						for dependecy in script['deps']:
							path = str(dependecy).split('/')
							new_script = path.pop()
							new_path = ""
							for path_segment in path:
								new_path += path_segment
							self.execute_command(new_path, current_working_directory, new_script)
					current_command = script['command']
					os.system(current_command)
					previous_absolute_path = os.path.abspath(previous_working_directory)
					os.chdir(previous_absolute_path)

			if script_found is False:
				raise Exception('build ' + str(script['name']) + ' is not a recognized command')
				return
				
		return

