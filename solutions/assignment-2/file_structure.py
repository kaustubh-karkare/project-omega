class FileStructure(object):

    @staticmethod
    def get_basic_file_structure():
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
        return FILE_STRUCTURE

    @staticmethod
    def get_file_structure_having_circular_dependency():
        FILE_STRUCTURE = {
            '.\\dirA\\build.json':
            r"""
            [
              {
                "name": "runA",
                "deps": ["dirB\\runB"],
                "command": "echo A"
              }
            ]
            """,
            '.\\dirB\\build.json':
            r"""
            [
              {
                "name": "runB",
                "deps": ["run"],
                "command": "echo B"
              }
            ]
            """,
            '.\\build.json':
            r"""
            [
              {
                "name": "run",
                "deps": ["dirA\\runA"],
                "command": "echo testing circular dependency"
              }
            ]
            """
        }
        return FILE_STRUCTURE

    def get_file_structure_having_undefined_dependency():
        FILE_STRUCTURE = {
            '.\\dirA\\build.json':
            r"""
            [
              {
                "name": "runA",
                "command": "echo A"
              }
            ]
            """,
            '.\\dirB\\build.json':
            r"""
            [
              {
                "name": "runB",
                "command": "echo B"
              }
            ]
            """,
            '.\\build.json':
            r"""
            [
              {
                "name": "run",
                "deps": ["dirA\\runA", "runB"],
                "command": "echo parent"
              }
            ]
            """
        }
        return FILE_STRUCTURE

    @staticmethod
    def get_file_structure_having_invalid_build_option():
        FILE_STRUCTURE = {
            '.\\dirA\\build.json':
            r"""
            [
              {
                "name": "runA",
                "command": "echo A"
              }
            ]
            """,
            '.\\dirB\\build.json':
            r"""
            [
              {
                "name": "runB",
                "command": "echo B"
              }
            ]
            """,
            '.\\build.json':
            r"""
            [
              {
                "name": "run",
                "deps": ["dirA\\runA", "dirB\\runB"],
                "command": "echo testing invalid build option"
              }
            ]
            """
        }
        return FILE_STRUCTURE

    @staticmethod
    def get_file_structure_having_multilevel_dependency():
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
            '.\\build.json':
            r"""
            [
              {
                "name": "run",
                "deps": ["dirA\\runA", "dirB\\runB"],
                "command": "echo testing multilevel dependency"
              }
            ]
            """,
            '.\\dirA\\build.json':
            r"""
            [
              {
                "name": "runA",
                "deps": ["dirC\\runC"],
                "command": "echo A"
              }
            ]
            """,
            '.\\dirB\\build.json':
            r"""
            [
              {
                "name": "runB",
                "deps": ["dirC\\runC"],
                "command": "echo B"
              }
            ]
            """,
            '.\\dirC\\build.json':
            r"""
            [
              {
                "name": "runC",
                "deps": ["dirD\\runD", "dirE\\runE"],
                "command": "echo C"
              }
            ]
            """,
            '.\\dirD\\build.json':
            r"""
            [
              {
                "name": "runD",
                "command": "echo D"
              }
            ]
            """,
            '.\\dirE\\build.json':
            r"""
            [
              {
                "name": "runE",
                "command": "echo E"
              }
            ]
            """
        }
        return FILE_STRUCTURE
