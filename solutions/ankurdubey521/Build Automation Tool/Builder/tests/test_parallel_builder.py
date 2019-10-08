import unittest
from Builder.lib.parallel_builder import ParallelBuilder
import subprocess
from multiprocessing import Process
from time import sleep
import pprint
import os
import tempfile
import shutil

MAX_THREAD_COUNT = 12


class TestParallelBuilder(unittest.TestCase):
    # The tests should work for any path inside the project
    def setUp(self):
        while os.path.basename(os.getcwd()) != 'Build Automation Tool':
            os.chdir('..')
        os.chdir('Builder/tests')

    def test_basic_shell_command(self):
        command = "echo 'Hello World!'"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(0, exit_code)

    def test_nonzero_exit_code_for_shell_command(self):
        command = "exit 1"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(1, exit_code)

    def test_dependency_graph_creation(self):
        local_path = os.getcwd() + '/test_builder_files/test_dependency_graph_creation'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder._explore_and_build_dependency_graph('Z', path)
            dependency_graph = {}
            for node_tuple in parallel_builder._dependency_graph:
                dependency_graph[node_tuple[0]] = []
                for item in parallel_builder._dependency_graph[node_tuple]:
                    dependency_graph[node_tuple[0]].append(item[0])
            pprint.pprint(dependency_graph, indent=4)
            correct_dependency_graph = {'X': ['Z'], 'XX': ['X'], 'XY': ['X'], 'Y': ['Z'], 'YX': ['Y'], 'YY': ['Y']}
            self.assertEqual(correct_dependency_graph, dependency_graph)

    def test_topological_sort_creation(self):
        local_path = os.getcwd() + '/test_builder_files/test_dependency_graph_creation'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('Z', path)
            toposort = [item[0] for item in parallel_builder._dependency_topological_sort]
            print(toposort)
            self.assertEqual(['XX', 'XY', 'YX', 'YY', 'X', 'Y', 'Z'], toposort)

    def test_basic_circular_dependency_throws_exception(self):
        local_path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency_throws_exception'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            self.assertRaises(
                parallel_builder.CircularDependencyException, parallel_builder.execute, 'A',
                path)

    def test_basic_circular_dependency2_throws_exception(self):
        local_path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency2_throws_exception'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            self.assertRaises(
                parallel_builder.CircularDependencyException, parallel_builder.execute, 'A',
                path)

    def test_compilation_basic(self):
        local_path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        with tempfile.TemporaryDirectory() as tmpdir:
            # RUN
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('run', path)
            exec_path = '"' + path + '/test.out' + '"'
            result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
            self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
            # CLEANUP
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder.execute('clean', path)
            self.assertFalse(os.path.isfile(path + "/test.out"))

    def test_commands_referenced_from_root(self):
        local_path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        with tempfile.TemporaryDirectory() as tmpdir:
            # RUN
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
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

    def test_parallel_sleep_commands(self):
        local_path = os.getcwd() + '/test_builder_files/test_parallel_sleep_commands'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            process = Process(target=parallel_builder.execute,
                              args=('Z', path))
            sleep(16)
            self.assertEqual(False, process.is_alive())

    def test_files_list_generation_adds_files_of_dependencies(self):
        local_path = os.getcwd() + '/test_builder_files/test_files_list_generation_adds_files_of_dependencies'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/test"
            shutil.copytree(local_path, path)
            parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
            parallel_builder._explore_and_build_dependency_graph('Z', path)
            file_list = parallel_builder._build_file_list_from_dependency_list('Z', path).sort()
            correct_file_list = [path + rel_path for rel_path in ['/z_file', '/X/x_file', '/Y/y_file']].sort()
            self.assertEqual(correct_file_list, file_list)


if __name__ == '__main__':
    unittest.main()
