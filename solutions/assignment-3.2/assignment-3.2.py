import argparse
import os
import time

from make import Make


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file_name',
        '-f',
        required=False,
        type=str,
        default='.descriptorfile',
        help='File Name of Descriptor File'
    )
    parser.add_argument(
        '--directory',
        '-d',
        required=False,
        type=str,
        default=os.getcwd(),
        help='Directory of Descriptor file'
    )
    parsed_argument = parser.parse_args()
    descriptor_path = os.path.join(
        parsed_argument.directory,
        parsed_argument.file_name
    )
    Make(descriptor_path).start()

if __name__ == '__main__':
    main()
