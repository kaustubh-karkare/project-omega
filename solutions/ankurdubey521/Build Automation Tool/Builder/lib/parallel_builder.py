from Builder.lib.buildconfig import BuildRule, BuildConfig
from Builder.lib.algorithms import TopologicalSort
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from typing import List
import subprocess


class ParallelBuilder:
    def __init__(self, root_dir_abs: str, max_threads: int):
        # Directed graph, (u, v) => v depends on u. u, v are pairs of (rule_name, rule_dir_abs)
        self._dependency_graph = {}
        self._dependency_topological_sort = []

        # List of (dependency_name, dependency_dir_abs) for each build rule
        self._dependency_list = {}

        self._root_dir_abs = root_dir_abs
        self._unresolved_commands = set()
        self._max_threads = max_threads

    class CircularDependencyException(Exception):
        pass

    def _explore_and_build_dependency_graph(self, command_name: str, command_dir_abs: str) -> None:
        # Remove Trailing '/' from paths if present
        if command_dir_abs.endswith('/'):
            command_dir_abs = command_dir_abs[:-1]
        if self._root_dir_abs.endswith('/'):
            self._root_dir_abs = self._root_dir_abs[:-1]

        # Parse build.json in current directory
        config = BuildConfig(command_dir_abs)
        command = config.get_command(command_name)

        # Mark the command's dependencies as unresolved
        self._unresolved_commands.add((command_name, command_dir_abs))

        # Process Dependencies
        try:
            deps = command.get_dependencies()
            for dep in deps:
                if dep.startswith('//'):
                    # Command path referenced from root directory
                    dep_dir_abs = self._root_dir_abs + '/' + dep[2:]
                    dep_dir_abs, dep_name = dep_dir_abs.rsplit('/', 1)
                elif '/' in dep:
                    # Command in child directory
                    dep_dir_abs, dep_name = dep.rsplit('/', 1)
                    dep_dir_abs = command_dir_abs + "/" + dep_dir_abs
                else:
                    # Command in same directory
                    dep_name = dep
                    dep_dir_abs = command_dir_abs

                dependency_tuple = (dep_name, dep_dir_abs)
                dependent_tuple = (command_name, command_dir_abs)

                # Update _dependency_graph
                if dependency_tuple not in self._dependency_graph:
                    self._dependency_graph[dependency_tuple] = []
                self._dependency_graph[dependency_tuple].append(dependent_tuple)

                # Update _dependency_list
                if dependent_tuple not in self._dependency_list:
                    self._dependency_list[dependent_tuple] = []
                self._dependency_list[dependent_tuple].append(dependency_tuple)

                # Check for circular dependencies
                if dependency_tuple in self._unresolved_commands:
                    raise self.CircularDependencyException(
                        "Detected a Circular Dependency between {}:{} and {}:{}"
                        .format(dep_dir_abs, dep_name, command_dir_abs, command_name))

                self._explore_and_build_dependency_graph(dep_name, dep_dir_abs)

        except BuildRule.NoDependenciesException:
            pass

    @staticmethod
    def _run_shell(command_string: str, cwd: str = '/', print_command: bool = False) -> subprocess.Popen:
        """Run Command and Return Exit Code. Optionally Print the command itself"""
        if print_command:
            print(command_string)
        return subprocess.Popen(command_string, shell=True, cwd=cwd)

    @staticmethod
    def _execute_rule_thread(command_name: str, command_string: str, command_dir_abs: str,
                             dependency_futures: List[Future]) -> int:
        for dependency_future in dependency_futures:
            return_value = dependency_future.result()
            # Stop Execution if Command Fails
            if return_value != 0:
                exit(-1)
        print("{}: [{}] in {}".format(str(datetime.now().time())[:8], command_name, command_dir_abs))
        return ParallelBuilder._run_shell(command_string, command_dir_abs, print_command=True).wait()

    def execute_build_rule_and_dependencies(self, command_name: str, command_dir_abs: str) -> None:
        # Create Dependency Graph
        print("\nExploring Dependencies...")
        self._explore_and_build_dependency_graph(command_name, command_dir_abs)
        print("\nDone exploring dependencies")

        # Generate Topological Sort
        self._dependency_topological_sort = TopologicalSort.sort(self._dependency_graph)
        # Handle case when no dependency exist (empty dependency graph => empty toposort)
        if len(self._dependency_topological_sort) == 0:
            self._dependency_topological_sort.append((command_name, command_dir_abs))

        # Dict[Tuple[name, abs_dir]: Futures]
        rule_to_futures = {}

        # Execute the Build Rules. starting from the deepest dependency
        print("\nExecuting Build Rules...")
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            for build_rule_tuple in self._dependency_topological_sort:
                (rule_name, rule_dir_abs) = build_rule_tuple
                rule_command_string = BuildConfig(rule_dir_abs).get_command(rule_name).get_command_string()
                dependency_futures = []
                if build_rule_tuple in self._dependency_list:
                    dependency_futures = \
                        [rule_to_futures[dependency] for dependency in self._dependency_list[build_rule_tuple]]
                thread = executor.submit(
                    ParallelBuilder._execute_rule_thread, rule_name, rule_command_string,
                    rule_dir_abs, dependency_futures)
                rule_to_futures[build_rule_tuple] = thread
        print("\nFinished Building")




