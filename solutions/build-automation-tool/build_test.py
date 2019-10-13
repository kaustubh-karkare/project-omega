import contextlib
import json
import os
import tempfile
import textwrap
import unittest

from build import Build


@contextlib.contextmanager
def create_and_change_to_tmpdir(working_directory):
    """Creates and switches directory to the a new temporary directory."""

    try:
        tmpdir = tempfile.TemporaryDirectory()
        os.chdir(tmpdir.name)
        yield tmpdir
    finally:
        os.chdir(working_directory)


class BuildTest(unittest.TestCase):

    def test_build(self):
        with create_and_change_to_tmpdir(os.getcwd()):
            build_file_1 = [{
                "name": "clean",
                "deps": ["algorithms/clean"],
                "command": "rm -f test.o && rm -f test.exe"
            }, {
                "name": "test",
                "files": ["test.cpp"],
                "command": "g++ -std=c++11 -c test.cpp"
            }, {
                "name": "run",
                "dependencies": [
                    "test", "algorithms/sort_bubble", "algorithms/sort_merge"
                ],
                "command": "g++ algorithms/sort_bubble.o\
                    algorithms/sort_merge.o test.o -o test.exe && ./test.exe"
            }]

            build_file_2 = [{
                "name": "clean",
                "command": "rm -f *.o"
            }, {
                "name": "sort_bubble",
                "files": ["sort_bubble.cpp"],
                "command": "g++ -c sort_bubble.cpp"
            }, {
                "name": "sort_merge",
                "files": ["sort_merge.cpp"],
                "command": "g++ -c sort_merge.cpp"
            }]

            with open('build.json', 'w') as build:
                json.dump(build_file_1, build)

            with open('test.cpp', 'w') as test:
                test.write(textwrap.dedent("""\
                #include <bits/stdc++.h>
                using namespace std;

                int main() {
                    return 0;
                }"""))

            os.mkdir('algorithms')

            with open('algorithms/build.json', 'w') as build:
                json.dump(build_file_2, build)

            with open('algorithms/sort_bubble.cpp', 'w') as sort_bubble:
                sort_bubble.write(textwrap.dedent("""
                #include <bits/stdc++.h>
                using namespace std;

                int bubble() {
                    return 0;
                }"""))

            with open('algorithms/sort_merge.cpp', 'w') as sort_merge:
                sort_merge.write(textwrap.dedent("""
                #include <bits/stdc++.h>
                using namespace std;

                int merge() {
                    return 0;
                }"""))

            build = Build(os.path.join(os.getcwd(), 'build.json'))

            build.build("test")
            assert os.path.exists("test.o")

            build.build("run")
            assert os.path.exists("test.exe")

            build.build("clean")
            assert not os.path.exists("test.o")
            assert not os.path.exists("test.exe")


if __name__ == '__main__':
    unittest.main()
