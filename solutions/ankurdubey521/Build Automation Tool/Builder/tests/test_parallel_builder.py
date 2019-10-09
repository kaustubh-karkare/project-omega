import unittest
from Builder.lib.parallel_builder import ParallelBuilder
from Builder.global_constants import GlobalConstants
from pathlib import Path
import subprocess
import time
import os
import tempfile
import json
import logging

MAX_THREAD_COUNT = 12

# Files for Tests
file_list = {
    "test_dependency_graph_creation": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                  {
                    "name": "Z",
                    "command": "echo \"Z\"",
                    "deps": ["X/X", "Y/Y"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "X",
                    "command": "echo \"X\"",
                    "deps": ["XX/XX", "XY/XY"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "XX",
                    "command": "echo \"XX\""
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "XY",
                        "command": "echo \"XY\""
                    }
                ]
            )
        }
        ,
        {
            "path": os.path.join("Y", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "Y",
                    "command": "echo \"Y\"",
                    "deps": ["YX/YX", "YY/YY"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YX",
                    "command": "echo \"YX\""
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YY",
                    "command": "echo \"YY\""
                  }
                ]
            )
        }
    ],
    "test_topological_sort_creation": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                  {
                    "name": "Z",
                    "command": "echo \"Z\"",
                    "deps": ["X/X", "Y/Y"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "X",
                    "command": "echo \"X\"",
                    "deps": ["XX/XX", "XY/XY"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "XX",
                    "command": "echo \"XX\""
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "XY",
                        "command": "echo \"XY\""
                    }
                ]
            )
        }
        ,
        {
            "path": os.path.join("Y", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "Y",
                    "command": "echo \"Y\"",
                    "deps": ["YX/YX", "YY/YY"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YX",
                    "command": "echo \"YX\""
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YY",
                    "command": "echo \"YY\""
                  }
                ]
            )
        }
    ],
    "test_basic_circular_dependency_throws_exception": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                  {
                    "name": "A",
                    "command": "echo \"A\"",
                    "deps": ["B"]
                  },
                  {
                    "name": "B",
                    "command": "echo \"B\"",
                    "deps": ["A"]
                  }
                ]
            )
        }
    ],
    "test_basic_circular_dependency2_throws_exception": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                    {
                        "name": "A",
                        "command": "echo \"A\"",
                        "deps": ["X/A"]
                    }
                ]
            )
        },
        {
            "path": os.path.join("X", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "A",
                        "command": "echo \"A\"",
                        "deps": ["//A"]
                    }
                ]
            )
        }
    ],
    "test_compilation_basic": [
        {
            "path": "test.cpp",
            "content": """
                #include<iostream>
                #include<vector>
                
                void sort_quick(std::vector<int>&);
                void sort_merge(std::vector<int>&);
                void sort_bubble(std::vector<int>&);
                
                void print(const std::vector<int> &vec) {
                    for(auto &x: vec) {
                        std::cout << x << " ";
                    }
                    std::cout << std::endl; 
                }
                
                int main() {
                    std::vector<int> a = {5, 4, 3, 2, 1}, b = a, c = a;
                    sort_quick(a);
                    sort_merge(b);
                    sort_bubble(c);
                    print(a);
                    print(b);
                    print(c);
                    return 0;
                }
            """
        },
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                    {
                        "name": "clean",
                        "deps": ["algorithms/clean"],
                        "files": ["test.cpp"],
                        "command": "rm -f test.o && rm -f test.out"
                    },
                    {
                        "name": "test",
                        "files": ["test.cpp"],
                        "command": "g++ -std=c++11 -c test.cpp"
                    },
                    {
                        "name": "run",
                        "deps": ["test", "algorithms/sort_bubble", "algorithms/sort_merge", "algorithms/sort_quick"],
                        "command": "g++ algorithms/sort_bubble.o algorithms/sort_merge.o " +
                                   "algorithms/sort_quick.o test.o -o test.out && ./test.out"
                    }
                ]
            )
        },
        {
            "path": os.path.join("algorithms", "sort_quick.cpp"),
            "content": """
                    #include<vector>
                    #include<algorithm>
                    
                    void sort_quick(std::vector<int> &arr) {
                        sort(arr.begin(), arr.end());
                    }
            """
        },
        {
            "path": os.path.join("algorithms", "sort_merge.cpp"),
            "content": """
                    #include<vector>
                    #include<algorithm>

                    void sort_merge(std::vector<int> &arr) {
                        sort(arr.begin(), arr.end());
                    }
            """
        },
        {
            "path": os.path.join("algorithms", "sort_bubble.cpp"),
            "content": """
                    #include<vector>
                    #include<algorithm>
                    
                    void sort_bubble(std::vector<int> &arr) {
                        sort(arr.begin(), arr.end());
                    }
            """
        },
        {
            "path": os.path.join("algorithms", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
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
            )
        }
    ],
    "test_commands_referenced_from_root": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                    {
                        "name": "clean",
                        "command": "rm output"
                    },
                    {
                        "name": "run",
                        "deps": ["B/run"],
                        "command": "echo \"run root\" >> output"
                    }
                ]

            )
        },
        {
            "path": os.path.join("B", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "clean",
                        "command": "echo \"clean B\""
                    },
                    {
                        "name": "run",
                        "deps": ["//A/run"],
                        "command": "echo \"run B\" >> ../output"
                    }
                ]
            )
        },
        {
            "path": os.path.join("A", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "clean",
                        "command": "echo \"clean A\""
                    },
                    {
                        "name": "run",
                        "command": "echo \"run A\" >> ../output"
                    }
                ]
            )
        },
    ],
    "test_parallel_sleep_commands": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                  {
                    "name": "Z",
                    "command": "sleep 5",
                    "deps": ["X/X", "Y/Y"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "X",
                    "command": "sleep 5",
                    "deps": ["XX/XX", "XY/XY"]
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "XX",
                    "command": "sleep 5"
                  }
                ]
            )
        },
        {
            "path": os.path.join("X", "XY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "XY",
                        "command": "sleep 5"
                    }
                ]
            )
        }
        ,
        {
            "path": os.path.join("Y", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "Y",
                    "command": "sleep 5"
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YX", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YX",
                    "command": "sleep 5"
                  }
                ]
            )
        },
        {
            "path": os.path.join("Y", "YY", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                  {
                    "name": "YY",
                    "command": "sleep 5"
                  }
                ]
            )
        }
    ],
    "test_files_list_generation_adds_files_of_dependencies": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                    {
                        "name": "Z",
                        "command": "sleep 5",
                        "deps": ["X/X", "Y/Y"],
                        "files": ["z_file"]
                    }
                ]
            )
        },
        {
            "path": os.path.join("Y", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "Y",
                        "command": "sleep 5",
                        "files": ["y_file"]
                    }
                ]
            )
        },
        {
            "path": os.path.join("X", GlobalConstants.CONFIG_FILE_NAME),
            "content": json.dumps(
                [
                    {
                        "name": "X",
                        "command": "sleep 5",
                        "files": ["x_file"]
                    }
                ]
            )
        }
    ],
    "test_failed_dependency": [
        {
            "path": GlobalConstants.CONFIG_FILE_NAME,
            "content": json.dumps(
                [
                    {
                        "name": "rule",
                        "command": "echo \"Built rule\"",
                        "deps": ["dep1", "dep2"]
                    },
                    {
                        "name": "dep1",
                        "command": "exit -1"
                    },
                    {
                        "name": "dep2",
                        "command": "exit 0"
                    }
                ]
            )
        }
    ]
}

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


def write_test_files(test_name: str, path: str) -> None:
    for file_dict in file_list[test_name]:
        file_path = os.path.join(path, file_dict["path"])
        dir_path = os.path.dirname(file_path)
        Path(dir_path).mkdir(exist_ok=True, parents=True)
        with open(file_path, "w") as file_handle:
            file_handle.write(file_dict["content"])


class TestParallelBuilder(unittest.TestCase):
    def test_basic_shell_command(self):
        command = "echo 'Hello World!'"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(0, exit_code)

    def test_nonzero_exit_code_for_shell_command(self):
        command = "exit 1"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(1, exit_code)

    def test_dependency_graph_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder._explore_and_build_dependency_graph('Z', path)
            dependency_graph = {}
            for node_tuple in parallel_builder._dependency_graph:
                dependency_graph[node_tuple[0]] = []
                for item in parallel_builder._dependency_graph[node_tuple]:
                    dependency_graph[node_tuple[0]].append(item[0])
            correct_dependency_graph = {'X': ['Z'], 'XX': ['X'], 'XY': ['X'], 'Y': ['Z'], 'YX': ['Y'], 'YY': ['Y']}
            self.assertEqual(correct_dependency_graph, dependency_graph)

    def test_topological_sort_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('Z', path)
            toposort = [item[0] for item in parallel_builder._topologically_sorted_build_rule_names]
            print(toposort)
            self.assertEqual(['XX', 'XY', 'YX', 'YY', 'X', 'Y', 'Z'], toposort)

    def test_basic_circular_dependency_throws_exception(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            self.assertRaises(
                parallel_builder.CircularDependencyException, parallel_builder.execute, 'A',
                path)
            self.assertFalse(parallel_builder.get_last_build_pass_status())

    def test_basic_circular_dependency2_throws_exception(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            self.assertRaises(
                parallel_builder.CircularDependencyException, parallel_builder.execute, 'A',
                path)
            self.assertFalse(parallel_builder.get_last_build_pass_status())

    def test_compilation_basic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # RUN
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('run', path)
            exec_path = '"' + path + '/test.out' + '"'
            result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
            self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
            # CLEANUP
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('clean', path)
            self.assertFalse(os.path.isfile(path + "/test.out"))
            self.assertTrue(parallel_builder.get_last_build_pass_status())

    def test_commands_referenced_from_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # RUN
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('run', path)
            output_file_path = path + '/output'
            with open(output_file_path) as file_handle:
                result = file_handle.readable()
            self.assertEqual(True, result)
            # CLEANUP
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('clean', path)
            self.assertFalse(os.path.isfile(path + "/output"))
            self.assertTrue(parallel_builder.get_last_build_pass_status())

    def test_parallel_sleep_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            start_time = time.time()
            parallel_builder.execute('Z', path)
            end_time = time.time()
            self.assertTrue(end_time - start_time < 16)
            self.assertTrue(parallel_builder.get_last_build_pass_status())

    def test_files_list_generation_adds_files_of_dependencies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder._explore_and_build_dependency_graph('Z', path)
            file_list = parallel_builder._build_file_list_from_dependency_list('Z', path).sort()
            correct_file_list = [path + rel_path for rel_path in ['/z_file', '/X/x_file', '/Y/y_file']].sort()
            self.assertEqual(correct_file_list, file_list)

    def test_failed_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test")
            write_test_files(self._testMethodName, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('rule', path)
            self.assertFalse(parallel_builder.get_last_build_pass_status())


if __name__ == '__main__':
    unittest.main()
