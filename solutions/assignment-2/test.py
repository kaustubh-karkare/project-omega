from build import Build, BuildAutomationError
from file_structure import FileStructure
from typing import List
import unittest
import tempfile
import json
import os


class TestBuildAutomation(unittest.TestCase):

    def create_file_structure(self, FILE_STRUCTURE, root) -> None:
        for files in FILE_STRUCTURE:
            dirs: List[str] = files.split('\\')
            filename: str = dirs.pop()
            path: str = root
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

    def test_basic_build_automation(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_basic_file_structure(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} run'.split())
            result = build.execute()
            self.assertEqual(result, 'Tested sort_bubble sort_merge sort_quick\r\n')
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, 'test.o')))
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, 'test.exe')))
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_bubble.o")))
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_merge.o")))
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_quick.o")))

            build = Build(f'--root={tmpdirname} clean'.split())
            result = build.execute()
            self.assertEqual(result, '')
            self.assertFalse(os.path.exists(os.path.join(tmpdirname, 'test.o')))
            self.assertFalse(os.path.exists(os.path.join(tmpdirname, 'test.exe')))
            self.assertFalse(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_bubble.o")))
            self.assertFalse(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_merge.o")))
            self.assertFalse(os.path.exists(os.path.join(tmpdirname, r"algorithms\sort_quick.o")))

    def test_circular_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_file_structure_having_circular_dependency(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} run'.split())
            with self.assertRaises(BuildAutomationError) as context:
                build.execute()
            self.assertEqual(str(context.exception), 'Error: Cyclic dependencies found')

    def test_undefined_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_file_structure_having_undefined_dependency(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} run'.split())
            with self.assertRaises(BuildAutomationError) as context:
                build.execute()
            self.assertEqual(str(context.exception), 'Error: run is dependent on runB, "runB" is an undefined dependency')

    def test_invalid_build_option(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_file_structure_having_invalid_build_option(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} runB'.split())
            with self.assertRaises(BuildAutomationError) as context:
                build.execute()
            self.assertEqual(str(context.exception), 'Error: Invalid rule "runB" provided')

    def test_multilevel_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_file_structure_having_multilevel_dependency(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} run'.split())
            result = build.execute()
            excepted_result = "D\r\nE\r\nC\r\nA\r\nB\r\ntesting multilevel dependency\r\n"
            self.assertEqual(result, excepted_result)

            build = Build(f'--root={tmpdirname} dirB\\runB'.split())
            result = build.execute()
            expected_result = 'D\r\nE\r\nC\r\nB\r\n'
            self.assertEqual(result, expected_result)

            build = Build(f'--root={tmpdirname} dirC\\runC'.split())
            result = build.execute()
            expected_result = 'D\r\nE\r\nC\r\n'
            self.assertEqual(result, expected_result)

    def test_watch(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_basic_file_structure(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} clean run --watch'.split())
            build.execute()

            with open(os.path.join(tmpdirname, r'algorithms\sort_bubble.cpp'), 'w') as sort_bubble:
                sort_bubble.write(r"""
                    # include<iostream>
                    void sort_bubble(){
                    std::cout<<"sort_bubble_modified";
                    }
                    """)
            result = build.check_and_maybe_execute()
            self.assertEqual(result, 'Tested sort_bubble_modified sort_merge sort_quick\r\n')

            with open(os.path.join(tmpdirname, r'algorithms\sort_merge.cpp'), 'w') as sort_merge:
                sort_merge.write(r"""
                    # include<iostream>
                    void sort_merge(){
                    std::cout<<"sort_merge_modified";
                    }
                    """)
            result = build.check_and_maybe_execute()
            self.assertEqual(result, 'Tested sort_bubble_modified sort_merge_modified sort_quick\r\n')

            with open(os.path.join(tmpdirname, r'test.cpp'), 'w') as test:
                test.write(r"""
                    # include<iostream>
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
            result = build.check_and_maybe_execute()
            self.assertEqual(result, '<Modified> Tested sort_bubble_modified sort_merge_modified sort_quick\r\n')

            # testing Build on modification of BUILD_FILE
            with open(os.path.join(tmpdirname, r'build.json'), 'r') as test:
                json_dict = json.loads(test.read())
                json_dict[2]["command"] = "echo Testing File Modification in BUILD_FILE"
                content = json.dumps(json_dict)
                with open(os.path.join(tmpdirname, r'build.json'), 'w') as json_file:
                    json_file.write(content)
            result = build.check_and_maybe_execute()
            self.assertEqual(result, 'Testing File Modification in BUILD_FILE\r\n')

    def test_ignore_files(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_file_structure(FileStructure.get_basic_file_structure(), root=tmpdirname)
            build = Build(f'--root={tmpdirname} clean run --watch --ignore .\\test.cpp'.split())
            build.execute()

            with open(os.path.join(tmpdirname, r'test.cpp'), 'w') as test:
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
            result = build.check_and_maybe_execute()
            self.assertEqual(result, "")  # Since test.cpp is set to be ignored, modification of test.cpp does not trigger any execution

            with open(os.path.join(tmpdirname, r'algorithms\sort_bubble.cpp'), 'w') as sort_bubble:
                sort_bubble.write(r"""
                    #include<iostream>
                    void sort_bubble(){
                    std::cout<<"sort_bubble_modified";
                    }
                    """)
            result = build.check_and_maybe_execute()
            self.assertEqual(result, 'Tested sort_bubble_modified sort_merge sort_quick\r\n')  # Modification in the test.cpp is not reflected as it is ignored even if modification in other files are made


if __name__ == '__main__':
    unittest.main()
