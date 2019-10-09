import os
import sys
import json
import argparse


def fun(current_working_directory, current_script):
	absolute_path = os.path.abspath(current_working_directory)
	os.chdir(absolute_path)
	with open(os.path.join("build.json")) as json_file:
		scripts = json.load(json_file)
		for script in scripts:
			if script['name'] == current_script:
				if 'deps' in script:
					dependecy = ""
					dependecy = str(dependecy)[2:len(str(dependecy))-2]
					path = str(dependecy).split('/')
					new_script = path.pop()
					new_path = ""
					for path_segment in path:
						new_path += path_segment
					fun(new_path, new_script)
				current_command = script['command']
				os.system(current_command)


if __name__ == '__main__':
	fun(os.getcwd(), 'clean')