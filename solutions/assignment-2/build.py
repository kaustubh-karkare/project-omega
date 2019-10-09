import os
import json
import logging
import argparse
import threading
import subprocess
from time import sleep
from graph import Graph, GraphError
from typing import Any, List, Dict, Optional


class BuildAutomationError(Exception):

    def __init__(self, message: str):
        self.message: str = 'Error: ' + message
        super(BuildAutomationError, self).__init__(self.message)


class File(object):
    """docstring for File"""

    def __init__(self, filename: str, is_BUILD_FILE: bool=False):
        self.filename: str = filename
        self.last_modified: float = os.path.getmtime(filename)
        self.is_BUILD_FILE: bool = is_BUILD_FILE

    def is_modified(self) -> bool:
        if os.path.getmtime(self.filename) != self.last_modified:
            self.last_modified = os.path.getmtime(self.filename)
            return True
        return False


class Rule(object):
    """rule stores all the possible build rules provided in build configuration files"""

    def __init__(self, properties: Dict[str, Any], command_path: str):
        self.name: str = properties['name']
        self.command: str = 'cd {} && {}'.format(command_path, properties['command'])
        self.filenames: List[str] = list()
        self.dependent_rulenames: List[str] = list()
        if 'deps' in properties:
            self.dependent_rulenames = properties['deps']
        if 'files' in properties:
            for filename in properties['files']:
                self.filenames.append(os.path.join(command_path, filename))

    def execute(self) -> str:
        process = subprocess.Popen(self.command.split(), stdout=subprocess.PIPE, shell=True)
        (out, err) = process.communicate()
        return out.decode()


class Build(object):
    """Build scans a given directory and stores all the possible build rules """

    BUILD_FILENAME = "build.json"

    def __init__(self, arguments: List[str]):
        self.logger = logging.getLogger()
        self.build_rules: Dict[str, Rule] = dict()
        self.build_files: Dict[str, File] = dict()
        self.build_arguments: Dict[str, Any] = self._parse(arguments)
        self.build_arguments['root'] = os.path.realpath(self.build_arguments['root'])
        self._scan(path=self.build_arguments['root'], relative_path='')
        self.set_ignored_files()
        self.watch_thread: Optional[Any] = None
        self.stop_watch = True

    def _parse(self, arguments: List[str]) -> Dict[str, Any]:
        parser = argparse.ArgumentParser(description='Process build rules')
        parser.add_argument('rules', nargs='*', type=str, help='A list of build rules')
        parser.add_argument('--root', type=str, default=r'.\\', help='Root directory where build is to be triggered')
        parser.add_argument('--watch', action='store_true', help='Status to build again on file modification')
        parser.add_argument('--poll', type=float, default=1, help='Time interval for checking the file modification status')
        parser.add_argument('--ignore', nargs='*', type=str, help='List of files not to be watched')
        return vars(parser.parse_args(arguments))

    def _scan(self, path: str, relative_path: str) -> None:
        for filename in os.listdir(path):
            file_path: str = os.path.join(path, filename)
            if os.path.isdir(file_path):
                self._scan(path=file_path, relative_path=os.path.join(relative_path, filename))
                continue
            if filename == self.BUILD_FILENAME:
                with open(file_path, 'r') as json_file:
                    try:
                        json_dict: Any = json.loads(json_file.read())
                    except ValueError:
                        raise BuildAutomationError(f'Decoding json build configuration file "{file_path}" failed')
                    for properties in json_dict:
                        properties['name'] = os.path.join(relative_path, properties['name'])
                        name = properties['name']
                        if name in self.build_rules:
                            raise BuildAutomationError(f'{name} has multifile entities in different build configuration files which conflicts')
                        self.build_rules[name] = Rule(properties=properties, command_path=path)
                        if self.build_rules[name].filenames:
                            for filename in self.build_rules[name].filenames:
                                if filename not in self.build_files:
                                    self.build_files[filename] = File(filename=filename)
                self.build_files[file_path] = File(filename=file_path, is_BUILD_FILE=True)

    def get_dependent_rulenames_for_executing_rule(self, rulename: str) -> List[str]:
        """Generating one dependency list for all the rules"""
        dependency_list: Dict[str, List[str]] = dict()
        for rule in self.build_rules:
            dependency_list[rule] = self.build_rules[rule].dependent_rulenames
        try:
            graph = Graph(dependency_list)
            all_dependencies: List[str] = graph.draft_first_search(rulename)
            all_dependencies.reverse()
        except GraphError as e:
            raise BuildAutomationError(e.message)
        return all_dependencies

    def get_dependent_rulenames_for_executing_changes_in_file(self, filename: str) -> List[str]:
        """Generating one supporter list for all the rules and files"""
        supporter_list: Dict[str, List[str]] = {key: list() for key in self.build_rules}
        for file_name in self.build_files:
            if not self.build_files[file_name].is_BUILD_FILE:
                supporter_list[file_name] = list()

        for rulename in self.build_rules:
            for dependent_rulename in self.build_rules[rulename].dependent_rulenames:
                supporter_list[dependent_rulename].append(rulename)
            for file_name in self.build_rules[rulename].filenames:
                supporter_list[file_name].append(rulename)
        try:
            graph = Graph(supporter_list)
            all_supporters: List[str] = graph.draft_first_search(filename)
        except GraphError as e:
            raise BuildAutomationError(e.message)
        all_supporters.pop(0)  # The first element being the filename is not executable and needs to be removed
        return all_supporters

    def execute(self) -> str:
        output = ''
        for rulename in self.build_arguments['rules']:
            if rulename not in self.build_rules:
                raise BuildAutomationError(f'Invalid rule "{rulename}" provided')
            dependent_rulenames = self.get_dependent_rulenames_for_executing_rule(rulename)
            for dependent_rulename in dependent_rulenames:
                output += self.build_rules[dependent_rulename].execute()
        return output

    def set_ignored_files(self) -> None:
        self.ignored_files: List[str] = list()
        if self.build_arguments['ignore']:
            for file in self.build_arguments['ignore']:
                self.ignored_files.append(os.path.join(self.build_arguments['root'], os.path.normpath(file)))

    def check_and_maybe_execute(self) -> str:
        output = ''
        for filename in self.build_files:
            if filename not in self.ignored_files:
                if self.build_files[filename].is_modified():
                    self.logger.info(f"Modification in file {filename} detected")
                    if self.build_files[filename].is_BUILD_FILE:
                        self.build_rules.clear()
                        self.build_files.clear()
                        self._scan(path=self.build_arguments['root'], relative_path='')
                        output += self.execute()
                    else:
                        dependent_rulenames = self.get_dependent_rulenames_for_executing_changes_in_file(filename)
                        for rulename in dependent_rulenames:
                            output += self.build_rules[rulename].execute()
        return output

    def start_watching(self) -> None:
        if not self.build_arguments['watch']:
            raise BuildAutomationError('Failed to start watch. Watch is not set to True for this build process.')
        if self.stop_watch:
            self.watch_thread = threading.Thread(target=self._thread_for_watching)
            self.stop_watch = False
            self.watch_thread.start()
        else:
            raise BuildAutomationError('A watch function is already running for this build process')

    def _thread_for_watching(self) -> None:
        while not self.stop_watch:
            sleep(self.build_arguments['poll'])
            output = self.check_and_maybe_execute()
            if output != '':
                self.logger.info(f"Automatic build result: {output}")

    def stop_watching(self) -> None:
        if not self.stop_watch:
            self.stop_watch = True
            self.watch_thread.join()
        else:
            raise BuildAutomationError('No Watch funtion running to stop')
