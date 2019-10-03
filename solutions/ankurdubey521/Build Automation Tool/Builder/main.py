from Builder.lib.builder import Builder
import argparse
import sys
import os


if __name__ == '__main__':
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument('build_rule', type=str)
    parser.add_argument('--watch', type=bool)
    args = parser.parse_args(sys.argv[1:])

    # Parse Command
    command = args.build_rule
    builder = Builder()
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.getcwd() + "/" + relative_path

    # TODO: Make root directory configurable

    try:
        if args.watch is None:
            builder.execute_build_rule(command, path, os.getcwd())
        else:
            # Watch files and run build rule on changes
            pass
    except Exception as e:
        print(e)

