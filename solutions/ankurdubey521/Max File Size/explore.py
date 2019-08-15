#!/bin/python3

# Ankur Dubey

import os
import sys

SHOW_FILES_SCANNED = False


class InvalidPathException(Exception):
    """Raise when Path does not exists in Filesystem"""


class NoFileFoundException(Exception):
    """Raise when Path does not contain any file"""


def max_files(path):
    # Returns maximum size and list of files having maximum size

    # Throw Error if path is invalid
    if not os.path.exists(path):
        raise InvalidPathException(path)

    max_size = 0
    max_file_paths = []
    directory_contains_file = False
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.stat(file_path).st_size
            if file_size > max_size:
                max_file_paths.clear()
                max_file_paths.append(file_path)
                max_size = file_size
                directory_contains_file = True
            elif file_size == max_size:
                max_file_paths.append(file_path)
                directory_contains_file = True
            if SHOW_FILES_SCANNED:
                print(file_path)

    # Throw error if path contains no file
    if not directory_contains_file:
        raise NoFileFoundException(path)
    return max_size, max_file_paths


def main():
    if len(sys.argv) == 1:
        print("Usage: explore <path>")
        print("Supports both relative and absolute paths")
        return
    max_size, max_file_paths = max_files(sys.argv[1])
    print("Maximum file size of {} bytes reported for following files:".format(max_size))
    for path in max_file_paths:
        print("{}".format(path))


if __name__ == "__main__":
    main()
