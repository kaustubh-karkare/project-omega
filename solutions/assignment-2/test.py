import os
import shutil
import unittest
import subprocess
from time import sleep
from threading import Thread


class Parallel_build_thread(Thread):
    """A thread implementation to run multiple build directories parallely"""

    def __init__(self, cmd: str):
        Thread.__init__(self)
        self.cmd: str = cmd
        self.output: str = ''

    def run(self):
        try:
            self.output = subprocess.check_output(self.cmd, shell=True)
        except subprocess.CalledProcessError as e:
            self.output = e.output


class TestBuildAutomation(unittest.TestCase):

    def create_file_structure(self, FILE_STRUCTURE, root):
        for files in FILE_STRUCTURE:
            dirs = files.split('\\')
            filename = dirs.pop()
            path = root
            for directory in dirs:
                path = os.path.join(path, directory)
            try:
                os.makedirs(path)
            except WindowsError:
                pass
            finally:
                path = os.path.join(path, filename)
                with open(path, 'w') as file_content:
                    file_content.write(FILE_STRUCTURE[files])

    def delete_file_structure(self, root):
        shutil.rmtree(root)

    def test_basic_build_automation(self):
        FILE_STRUCTURE = {
            'algorithms\\sort_bubble.cpp':
            r"""
            #include<iostream>
            void sort_bubble(){
                std::cout<<"sort_bubble";
            }
            """,

            'algorithms\\sort_merge.cpp':
            r"""
            #include<iostream>
            void sort_merge(){
                std::cout<<"sort_merge";
            }
            """,

            'algorithms\\sort_quick.cpp':
            r"""
            #include<iostream>
            void sort_quick(){
                std::cout<<"sort_quick";
            }
            """,

            'algorithms\\build.json':
            r"""
            [
              {
                "name": "clean",
                "command": "rm -f *.o"
              },
              {
                "name": "sort_bubble",
                "files": ["sort_bubble.cpp"],
                "command": "g++ -c sort_bubble.cpp"
              },
              {
                "name": "sort_merge",
                "files": ["sort_merge.cpp"],
                "command": "g++ -c sort_merge.cpp"
              },
              {
                "name": "sort_quick",
                "files": ["sort_quick.cpp"],
                "command": "g++ -c sort_quick.cpp"
              }
            ]
            """,
            'test.cpp':
            r"""
            #include<iostream>
            void sort_bubble();
            void sort_merge();
            void sort_quick();
            int main(){
                std::cout<<"Tested ";
                sort_bubble();
                std::cout<<" ";
                sort_merge();
                std::cout<<" ";
                sort_quick();
                std::cout<<"\n";
            }
            """,
            'build.json':
            r"""
            [
              {
                "name": "clean",
                "deps": ["algorithms\\clean"],
                "command": "rm -f test.o && rm -f test.exe"
              },
              {
                "name": "test",
                "files": ["test.cpp"],
                "command": "g++ -std=c++11 -c test.cpp"
              },
              {
                "name": "run",
                "deps": ["test", "algorithms\\sort_bubble", "algorithms\\sort_merge", "algorithms\\sort_quick"],
                "command": "g++ algorithms\\sort_bubble.o algorithms\\sort_merge.o algorithms\\sort_quick.o test.o -o test.exe && .\\test.exe"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')
        cmd = r'python build.py --root=~\tmp\ clean run'
        result = subprocess.check_output(cmd, shell=True)
        self.assertEqual(result, b'Tested sort_bubble sort_merge sort_quick\r\n')
        assert(os.path.exists(r".\tmp\test.o"))
        assert(os.path.exists(r".\tmp\test.exe"))
        assert(os.path.exists(r".\tmp\algorithms\sort_bubble.o"))
        assert(os.path.exists(r".\tmp\algorithms\sort_merge.o"))
        assert(os.path.exists(r".\tmp\algorithms\sort_quick.o"))

        cmd = r'python build.py --root=~\tmp\ algorithms\clean'
        result = subprocess.check_output(cmd, shell=True)
        self.assertEqual(result, b'')
        assert(os.path.exists(r".\tmp\test.o"))
        assert(os.path.exists(r".\tmp\test.exe"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_bubble.o"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_merge.o"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_quick.o"))

        cmd = r'python build.py --root=~\tmp\ clean'
        result = subprocess.check_output(cmd, shell=True)
        self.assertEqual(result, b'')
        assert(not os.path.exists(r".\tmp\test.o"))
        assert(not os.path.exists(r".\tmp\test.exe"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_bubble.o"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_merge.o"))
        assert(not os.path.exists(r".\tmp\algorithms\sort_quick.o"))

        self.delete_file_structure(root='tmp')

    def test_circular_dependency(self):
        FILE_STRUCTURE = {
            'dirA\\build.json':
            r"""
            [
              {
                "name": "A",
                "deps": ["dirB\\B"],
                "command": "echo A"
              }
            ]
            """,
            'dirB\\build.json':
            r"""
            [
              {
                "name": "B",
                "deps": ["parent"],
                "command": "echo B"
              }
            ]
            """,
            'build.json':
            r"""
            [
              {
                "name": "parent",
                "deps": ["dirA\\A"],
                "command": "echo parent"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')

        cmd = r'python build.py --root=~\tmp\ parent'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'Error: Cyclic dependencies found.\r\n')

        self.delete_file_structure(root='tmp')

    def test_undefined_dependency(self):
        FILE_STRUCTURE = {
            'dirA\\build.json':
            r"""
            [
              {
                "name": "A",
                "command": "echo A"
              }
            ]
            """,
            'dirB\\build.json':
            r"""
            [
              {
                "name": "B",
                "command": "echo B"
              }
            ]
            """,
            'build.json':
            r"""
            [
              {
                "name": "parent",
                "deps": ["dirA\\A", "B"],
                "command": "echo parent"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')

        cmd = r'python build.py --root=~\tmp\ parent'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'Error: Undefined dependencies found "B".\r\n')

        self.delete_file_structure(root='tmp')

    def test_invalid_build_option(self):
        FILE_STRUCTURE = {
            'dirA\\build.json':
            r"""
            [
              {
                "name": "A",
                "command": "echo A"
              }
            ]
            """,
            'dirB\\build.json':
            r"""
            [
              {
                "name": "B",
                "command": "echo B"
              }
            ]
            """,
            'build.json':
            r"""
            [
              {
                "name": "parent",
                "deps": ["dirA\\A", "dirB\\B"],
                "command": "echo parent"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')

        cmd = r'python build.py --root=~\tmp\ B'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'Error: Invalid option "B" provided.\r\n')

        self.delete_file_structure(root='tmp')

    def test_multilevel_dependency(self):
        """
                parent
                /   \
               A     B
                \   /
                  C
                /   \
               D     E
        """
        FILE_STRUCTURE = {
            'build.json':
            r"""
            [
              {
                "name": "parent",
                "deps": ["dirA\\A", "dirB\\B"],
                "command": "echo parent"
              }
            ]
            """,
            'dirA\\build.json':
            r"""
            [
              {
                "name": "A",
                "deps": ["dirC\\C"],
                "command": "echo A"
              }
            ]
            """,
            'dirB\\build.json':
            r"""
            [
              {
                "name": "B",
                "deps": ["dirC\\C"],
                "command": "echo B"
              }
            ]
            """,
            'dirC\\build.json':
            r"""
            [
              {
                "name": "C",
                "deps": ["dirD\\D", "dirE\\E"],
                "command": "echo C"
              }
            ]
            """,
            'dirD\\build.json':
            r"""
            [
              {
                "name": "D",
                "command": "echo D"
              }
            ]
            """,
            'dirE\\build.json':
            r"""
            [
              {
                "name": "E",
                "command": "echo E"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')

        cmd = r'python build.py --root=~\tmp\ parent'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'D\r\nE\r\nC\r\nA\r\nB\r\nparent\r\n')

        cmd = r'python build.py --root=~\tmp\ dirB\B'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'D\r\nE\r\nC\r\nB\r\n')

        cmd = r'python build.py --root=~\tmp\ dirC\C'
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b'D\r\nE\r\nC\r\n')

        self.delete_file_structure(root='tmp')

    def test_watch(self):
        FILE_STRUCTURE = {
            'algorithms\\sort_bubble.cpp':
            r"""
            #include<iostream>
            void sort_bubble(){
                std::cout<<"sort_bubble";
            }
            """,

            'algorithms\\sort_merge.cpp':
            r"""
            #include<iostream>
            void sort_merge(){
                std::cout<<"sort_merge";
            }
            """,

            'algorithms\\sort_quick.cpp':
            r"""
            #include<iostream>
            void sort_quick(){
                std::cout<<"sort_quick";
            }
            """,

            'algorithms\\build.json':
            r"""
            [
              {
                "name": "clean",
                "command": "rm -f *.o"
              },
              {
                "name": "sort_bubble",
                "files": ["sort_bubble.cpp"],
                "command": "g++ -c sort_bubble.cpp"
              },
              {
                "name": "sort_merge",
                "files": ["sort_merge.cpp"],
                "command": "g++ -c sort_merge.cpp"
              },
              {
                "name": "sort_quick",
                "files": ["sort_quick.cpp"],
                "command": "g++ -c sort_quick.cpp"
              }
            ]
            """,
            'test.cpp':
            r"""
            #include<iostream>
            void sort_bubble();
            void sort_merge();
            void sort_quick();
            int main(){
                std::cout<<"Tested ";
                sort_bubble();
                std::cout<<" ";
                sort_merge();
                std::cout<<" ";
                sort_quick();
                std::cout<<"\n";
            }
            """,
            'build.json':
            r"""
            [
              {
                "name": "clean",
                "deps": ["algorithms\\clean"],
                "command": "rm -f test.o && rm -f test.exe"
              },
              {
                "name": "test",
                "files": ["test.cpp"],
                "command": "g++ -std=c++11 -c test.cpp"
              },
              {
                "name": "run",
                "deps": ["test", "algorithms\\sort_bubble", "algorithms\\sort_merge", "algorithms\\sort_quick"],
                "command": "g++ algorithms\\sort_bubble.o algorithms\\sort_merge.o algorithms\\sort_quick.o test.o -o test.exe && .\\test.exe"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')
        build_1 = Parallel_build_thread(r'python build.py --root=~\tmp\ clean run --watch=true')
        build_1.start()
        sleep(1)
        with open(r'tmp\algorithms\sort_bubble.cpp', 'w') as sort_bubble:
            sort_bubble.write(r"""
                #include<iostream>
                void sort_bubble(){
                std::cout<<"sort_bubble_modified";
                }
                """)
        sleep(10)
        with open(r'tmp\algorithms\sort_merge.cpp', 'w') as sort_merge:
            sort_merge.write(r"""
                #include<iostream>
                void sort_merge(){
                std::cout<<"sort_merge_modified";
                }
                """)
        sleep(10)
        with open(r'tmp\test.cpp', 'w') as test:
            test.write(r"""
                #include<iostream>
                void sort_bubble();
                void sort_merge();
                void sort_quick();
                int main(){
                    std::cout<<"<Modified> Tested ";
                    sort_bubble();
                    std::cout<<" ";
                    sort_merge();
                    std::cout<<" ";
                    sort_quick();
                    std::cout<<"\n";
                }
                """)
        sleep(10)

        build_2 = Parallel_build_thread(r'python build.py --root=~\tmp\ --watch=false')
        build_2.start()

        build_1.join()
        build_2.join()

        self.assertEqual(build_1.output, b'Tested sort_bubble sort_merge sort_quick\r\nTested sort_bubble_modified sort_merge sort_quick\r\nTested sort_bubble_modified sort_merge_modified sort_quick\r\n<Modified> Tested sort_bubble_modified sort_merge_modified sort_quick\r\n')
        self.delete_file_structure(root='tmp')

    def test_ignore_files(self):
        FILE_STRUCTURE = {
            'algorithms\\sort_bubble.cpp':
            r"""
            #include<iostream>
            void sort_bubble(){
                std::cout<<"sort_bubble";
            }
            """,

            'algorithms\\sort_merge.cpp':
            r"""
            #include<iostream>
            void sort_merge(){
                std::cout<<"sort_merge";
            }
            """,

            'algorithms\\sort_quick.cpp':
            r"""
            #include<iostream>
            void sort_quick(){
                std::cout<<"sort_quick";
            }
            """,

            'algorithms\\build.json':
            r"""
            [
              {
                "name": "clean",
                "command": "rm -f *.o"
              },
              {
                "name": "sort_bubble",
                "files": ["sort_bubble.cpp"],
                "command": "g++ -c sort_bubble.cpp"
              },
              {
                "name": "sort_merge",
                "files": ["sort_merge.cpp"],
                "command": "g++ -c sort_merge.cpp"
              },
              {
                "name": "sort_quick",
                "files": ["sort_quick.cpp"],
                "command": "g++ -c sort_quick.cpp"
              }
            ]
            """,
            'test.cpp':
            r"""
            #include<iostream>
            void sort_bubble();
            void sort_merge();
            void sort_quick();
            int main(){
                std::cout<<"Tested ";
                sort_bubble();
                std::cout<<" ";
                sort_merge();
                std::cout<<" ";
                sort_quick();
                std::cout<<"\n";
            }
            """,
            'build.json':
            r"""
            [
              {
                "name": "clean",
                "deps": ["algorithms\\clean"],
                "command": "rm -f test.o && rm -f test.exe"
              },
              {
                "name": "test",
                "files": ["test.cpp"],
                "command": "g++ -std=c++11 -c test.cpp"
              },
              {
                "name": "run",
                "deps": ["test", "algorithms\\sort_bubble", "algorithms\\sort_merge", "algorithms\\sort_quick"],
                "command": "g++ algorithms\\sort_bubble.o algorithms\\sort_merge.o algorithms\\sort_quick.o test.o -o test.exe && .\\test.exe"
              }
            ]
            """
        }
        self.create_file_structure(FILE_STRUCTURE, root='tmp')
        build_1 = Parallel_build_thread(r'python build.py --root=~\tmp\ clean run --watch=true --ignore ~\tmp\test.cpp')
        build_1.start()
        sleep(1)
        with open(r'tmp\test.cpp', 'w') as test:
            test.write(r"""
                #include<iostream>
                void sort_bubble();
                void sort_merge();
                void sort_quick();
                int main(){
                    std::cout<<"<Modified> Tested ";
                    sort_bubble();
                    std::cout<<" ";
                    sort_merge();
                    std::cout<<" ";
                    sort_quick();
                    std::cout<<"\n";
                }
                """)
        sleep(10)
        with open(r'tmp\algorithms\sort_bubble.cpp', 'w') as sort_bubble:
            sort_bubble.write(r"""
                #include<iostream>
                void sort_bubble(){
                std::cout<<"sort_bubble_modified";
                }
                """)
        sleep(10)

        build_2 = Parallel_build_thread(r'python build.py --root=~\tmp\ --watch=false')
        build_2.start()

        build_1.join()
        build_2.join()

        self.assertEqual(build_1.output, b'Tested sort_bubble sort_merge sort_quick\r\nTested sort_bubble_modified sort_merge sort_quick\r\n')
        self.delete_file_structure(root='tmp')


if __name__ == '__main__':

    unittest.main()

# python build.py --root=~\test1\ --watch=true clean run
