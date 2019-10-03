from Builder.lib.builder import Builder
import sys
import os


if __name__ == '__main__':
    command = sys.argv[1]
    builder = Builder()
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.getcwd() + "/" + relative_path
    # TODO: Make root directory configurable
    Builder.execute_build_rule(command, path, os.getcwd())
