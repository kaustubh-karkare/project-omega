import argparse
import os
import sys

from Builder.lib.default_logger import DefaultLogger
from Builder.lib.parallel_builder import ParallelBuilder

if __name__ == '__main__':
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument('build_rule', type=str)
    parser.add_argument('--watch', action="store_true")
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--max-threads', type=int)
    args = parser.parse_args(sys.argv[1:])

    logger = DefaultLogger.get_instance()

    # Parse Command
    command = args.build_rule
    root_dir = ""
    if args.root_dir is not None:
        root_dir = args.root_dir
    else:
        root_dir = os.getcwd()

    builder = ParallelBuilder(root_dir, args.max_threads, logger)
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.path.join(root_dir, relative_path)

    try:
        builder.execute(command, path, args.watch)
    except Exception as e:
        print(e)

