""" Parallel Builder: Handles execution of build rules and associated dependencies in parallel (whenever possible)
The execute() method is exposed as the interface for executing build rules.
The directory structure is explored to create a dependency graph, and a topological sort is
constructed on it. Starting from the deepest dependency, processes are spawned using Popen calls
and threads are assigned to watch for their completion.

"""


import logging
import os
import subprocess
from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from typing import Dict, List

from Builder.lib.algorithms import TopologicalSort
from Builder.lib.buildconfig import BuildConfig
from Builder.lib.file_watcher import FileWatcher


class ParallelBuilder:
    def __init__(self, root_dir_abs: str, max_threads: int, logger: logging.Logger):
        """ Constructor
        :param root_dir_abs: Absolute path of directory which is to b considered as root (or '//')
        :param max_threads: Max no. of threads to spawn while processing dependencies
        :param logger: logger object
        """
        # Config
        self._max_threads = max_threads
        self._root_dir_abs = root_dir_abs
        # Remove Trailing '/' from paths if present
        if self._root_dir_abs.endswith('/'):
            self._root_dir_abs = self._root_dir_abs[:-1]

        # Directed graph, (u, v) => v depends on u. u, v are pairs of (rule_name, rule_dir_abs)
        # Used for generating Topological Sort
        self._rule_to_dependency_graph_adjlist = {}
        self._topologically_sorted_build_rule_names = []

        # Boolean representing status of last build
        self._last_build_passed = False

        # List of (dependency_name, dependency_dir_abs) for each build rule
        self._rule_to_dependency_list = {}

        # Logger
        self.logger = logger

        # Space for rough work :P
        self._unresolved_commands = set()

    class CircularDependencyException(Exception):
        pass

    def _reset_state(self):
        """Resets state of Parallel Builder for new run"""
        # Directed graph, (u, v) => v depends on u. u, v are pairs of (rule_name, rule_dir_abs)
        # Used for generating Topological Sort
        self._rule_to_dependency_graph_adjlist = {}
        self._topologically_sorted_build_rule_names = []

        # List of (dependency_name, dependency_dir_abs) for each build rule
        self._rule_to_dependency_list = {}

        # Space for rough work :P
        self._unresolved_commands = set()

    def get_last_build_pass_status(self) -> bool:
        return self._last_build_passed

    def _explore_and_build_dependency_graph(self, build_rule_name: str, build_dir_abs: str) -> None:
        """ Populates self._rule_to_dependency_graph_adjlist and
        self._rule_to_dependency_list and checks for CircularDependencies
        :param build_rule_name: .
        :param build_dir_abs: Directory which contains build.config
        """

        # Parse build.json in current directory
        config = BuildConfig.load_from_build_directory(build_dir_abs)
        build_rule = config.get_build_rule(build_rule_name)

        # Mark the command's dependencies as unresolved
        self._unresolved_commands.add((build_rule_name, build_dir_abs))

        # Process Dependencies
        deps = build_rule.get_dependencies()
        for dep in deps:
            if dep.startswith('//'):
                # Command path referenced from root directory
                dep_dir_abs = os.path.join(self._root_dir_abs, dep[2:])
                dep_dir_abs, dep_name = dep_dir_abs.rsplit('/', 1)
            elif '/' in dep:
                # Command in child directory
                dep_dir_abs, dep_name = dep.rsplit('/', 1)
                dep_dir_abs = os.path.join(build_dir_abs, dep_dir_abs)
            else:
                # Command in same directory
                dep_name = dep
                dep_dir_abs = build_dir_abs

            dependency_tuple = (dep_name, dep_dir_abs)
            dependent_tuple = (build_rule_name, build_dir_abs)

            # Update _rule_to_dependency_graph_adjlist
            if dependency_tuple not in self._rule_to_dependency_graph_adjlist:
                self._rule_to_dependency_graph_adjlist[dependency_tuple] = []
            self._rule_to_dependency_graph_adjlist[dependency_tuple].append(dependent_tuple)

            # Update _rule_to_dependency_list
            if dependent_tuple not in self._rule_to_dependency_list:
                self._rule_to_dependency_list[dependent_tuple] = []
            self._rule_to_dependency_list[dependent_tuple].append(dependency_tuple)

            # Check for circular dependencies
            if dependency_tuple in self._unresolved_commands:
                self._last_build_passed = False
                raise self.CircularDependencyException(
                    "Detected a Circular Dependency between {}:{} and {}:{}"
                    .format(dep_dir_abs, dep_name, build_dir_abs, build_rule_name))

            self._explore_and_build_dependency_graph(dep_name, dep_dir_abs)

    def _build_file_list_from_dependency_list(self, build_rule_name: str, build_dir_abs: str) -> List[str]:
        """" Uses self._rule_to_dependency_list to generate a list of files which build_rule_name or it's dependencies reference
             self._explore_and_build_dependency_graph must be run before to populate self._rule_to_dependency_list
        :param build_rule_name: .
        :param build_dir_abs: Directory which contains build.config
        :return: List of absolute paths of files
        """
        file_list = []
        visited = set()
        queue = Queue()
        queue.put((build_rule_name, build_dir_abs))
        visited.add((build_rule_name, build_dir_abs))

        # BFS
        while not queue.empty():
            rule_name, rule_dir_abs = queue.get()
            rule_files_rel_path = \
                BuildConfig.load_from_build_directory(rule_dir_abs).get_build_rule(rule_name).get_files()
            # Get absolute paths of files and add to file_list
            rules_files_abs_path = [os.path.join(rule_dir_abs, path) for path in rule_files_rel_path]
            file_list.extend(rules_files_abs_path)

            if (rule_name, rule_dir_abs) in self._rule_to_dependency_list:
                for dep in self._rule_to_dependency_list[(rule_name, rule_dir_abs)]:
                    if dep not in visited:
                        visited.add(dep)
                        queue.put(dep)
                    else:
                        self._last_build_passed = False
                        raise ParallelBuilder.CircularDependencyException()
        return file_list

    def _run_shell(self, command_string: str, cwd: str = '/', print_command: bool = False) -> subprocess.Popen:
        """ Spawns a process to run the command
        :param command_string: full shell command to be run
        :param cwd: working directory
        :param print_command: specify True if command_string is to be printed with output
        :return: Popen object of spawned process
        """
        if print_command:
            self.logger.info(command_string)
        return subprocess.Popen(command_string, shell=True, cwd=cwd)

    def _execute_rule_thread(self, build_rule_name: str, command_string: str, build_dir_abs: str,
                             dependency_futures: Dict[str, Future] = {}) -> int:
        """ Waits for dependencies to finish executing, spawns a process for executing build_rule_name.
            This function is meant to be spawned as a separate thread for parallel execution
        :param build_rule_name: .
        :param command_string: full shell command to be run
        :param build_dir_abs:  Directory which contains build.config
        :param dependency_futures: Dict of [dep_name to Future] of spawned threads for running dependencies.
                                   Used for waiting until deps have finished executing
        :return: return value of process
        """
        for dependency_name in dependency_futures:
            return_value = dependency_futures[dependency_name].result()
            # Stop Execution if Command Fails
            if return_value != 0:
                self.logger.error("Building {} failed with exit code {}".format(dependency_name, return_value))
                return -1
        self.logger.info("[{}] in {}".format(build_rule_name, build_dir_abs))
        return self._run_shell(command_string, build_dir_abs, print_command=True).wait()

    def _execute_build_rule_and_dependencies(self) -> bool:
        """ Main execution logic
        :return: boolean indicating build success of build rule
        """
        # Dict[Tuple[name, abs_dir]: Futures]
        rule_to_futures = {}

        # Flags for indicating overall build status
        overall_build_success = True
        build_failed_for_dependency = False

        # Execute the Build Rules. starting from the deepest dependency
        self.logger.info("Executing Build Rules...")
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            for build_rule_tuple in self._topologically_sorted_build_rule_names:
                if not build_failed_for_dependency:
                    (rule_name, rule_dir_abs) = build_rule_tuple
                    rule_command_string = \
                        BuildConfig.load_from_build_directory(rule_dir_abs).get_build_rule(rule_name).get_command()

                    # Generate Dict for Popen of objects of Dependencies
                    dependency_futures = {}
                    if build_rule_tuple in self._rule_to_dependency_list:
                        for (dep_name, dep_dir_abs) in self._rule_to_dependency_list[build_rule_tuple]:
                            dependency_futures[dep_name] = rule_to_futures[(dep_name, dep_dir_abs)]

                    # Spawn the process for executing build rules and it's dependencies
                    # If a dependency fails during execution, build_failed_for_dependency will be set as True
                    # Cease operation at that moment
                    def build_success_validator(future: Future) -> None:
                        if future.result() != 0:
                            global build_failed_for_dependency, overall_build_success
                            build_failed_for_dependency = True
                            overall_build_success = False

                    thread = executor.submit(
                        self._execute_rule_thread, rule_name, rule_command_string, rule_dir_abs,
                        dependency_futures)
                    thread.add_done_callback(build_success_validator)
                    rule_to_futures[build_rule_tuple] = thread

        # Verify that all build rules succeeded (exited with 0)
        for rule_tuple in rule_to_futures:
            if rule_to_futures[rule_tuple].result() != 0:
                overall_build_success = False

        if overall_build_success:
            self.logger.info("Build Succeeded")
        else:
            self.logger.error("Build Failed")
        return overall_build_success

    def execute(self, build_rule_name: str, build_dir_abs: str, watch_for_file_changes=False) -> None:
        """ Interface for ParallelBuilder.
        :param build_rule_name: .
        :param build_dir_abs: Directory which contains build.config
        :param watch_for_file_changes: if set True it spawns a daemon listening for any changes in files referenced
                                        by the command or it's dependencies. File changes result in the build rule
                                        being re-run
        """
        self._reset_state()

        # Create Dependency Graph
        self.logger.info("Exploring Dependencies...")
        self._explore_and_build_dependency_graph(build_rule_name, build_dir_abs)
        self.logger.info("Done exploring dependencies")

        # Generate Topological Sort
        self._topologically_sorted_build_rule_names = TopologicalSort.sort(self._rule_to_dependency_graph_adjlist)
        # Handle case when no dependency exist (no dependency => no edge => empty dependency graph => empty toposort)
        if len(self._topologically_sorted_build_rule_names) == 0:
            self._topologically_sorted_build_rule_names.append((build_rule_name, build_dir_abs))

        if watch_for_file_changes:
            file_list_abs = self._build_file_list_from_dependency_list(build_rule_name, build_dir_abs)

            def callable_build_rule_executor():
                self._last_build_passed = self._execute_build_rule_and_dependencies()
            FileWatcher.watch_and_execute(file_list_abs, callable_build_rule_executor, self.logger)
        else:
            self._last_build_passed = self._execute_build_rule_and_dependencies()



