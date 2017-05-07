import argparse
from cppcompileutility import CompileCppFiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--directory',
        '-d',
        required=True,
        type=str,
        help='Directory path to compile cpp files'
    )
    parsed_option = parser.parse_args()
    CompileCppFiles(directory=parsed_option.directory)

if __name__ == '__main__':
    main()
