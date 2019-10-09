from Builder.lib.parallel_builder import ParallelBuilder
import argparse
import logging
import sys
import os


if __name__ == '__main__':
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument('build_rule', type=str)
    parser.add_argument('--watch', action="store_true")
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--max-threads', type=int)
    args = parser.parse_args(sys.argv[1:])

    # Configure Logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt="%H:%M:%S"))
    logger.addHandler(debug_handler)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S"))
    logger.addHandler(error_handler)

    # Parse Command
    command = args.build_rule
    root_dir = ""
    if args.root_dir is not None:
        root_dir = args.root_dir
    else:
        root_dir = os.getcwd()

    builder = ParallelBuilder(root_dir, args.max_threads)
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.path.join(root_dir, relative_path)

    try:
        builder.execute(command, path, args.watch)
    except Exception as e:
        print(e)

