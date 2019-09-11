import os
import sys
import json
import argparse
from graph import Graph, GraphError
from typing import Any, List, Dict
from time import sleep


class BuildAutomationError(Exception):

    def __init__(self, message: str):
        super(BuildAutomationError, self).__init__(message)
        self.message: str = f'Error: {message}.'


class File(object):
    """docstring for File"""

    def __init__(self, filename: str):
        self.filename: str = filename
        self.last_modified: float = os.path.getmtime(filename)
        self.dependent_options: List[Option] = list()   # list of options which are directly dependent on this file
        self.all_dependent_options: List[Option] = list()   # the order of all the options which needs to be executed if this file modifies

    def is_modified(self) -> bool:
        if os.path.getmtime(self.filename) != self.last_modified:
            self.last_modified = os.path.getmtime(self.filename)
            return True
        return False

    def rebuild(self) -> None:
        for option in self.all_dependent_options:
            os.system(option.command)


class Option(object):
    """Option stores all the possible build options provided in build configuration files"""

    def __init__(self, properties: Dict[str, Any], command_path: str):
        self.name: str = properties['name']
        self.command: str = 'cd {} && {}'.format(command_path, properties['command'])
        self.all_dependent_options: List[Option] = list()   # the order of all the options which needs to be executed for execution of this option
        self.all_supporter_options: List[Option] = list()

    def execute(self) -> None:
        for option in self.all_dependent_options:
            os.system(option.command)


class Build(object):
    """Build scans a given directory and stores all the possible build options """

    BUILD_FILENAME = "build.json"

    """
    This file will store the map of all the running build process in the form of {root directory address: processID}
    Whenever a build process is triggered, this file will be used to lookup for any running bulid process in the same directory
    If there is any existing process running, we will stop it and run the current process (also making an entry in process.json about current process)
    """
    PROCESS_FILENAME = "process.json"

    def __init__(self, arguments: List[str]):
        self.build_arguments: Dict[str, Any] = self.parse(arguments)
        self.build_options: Dict[str, Option] = dict()
        self.build_files: Dict[str, File] = dict()
        self.dependency_list: Dict[str, List[str]] = dict()
        self.build_arguments['root'] = self.find_path(self.build_arguments['root'])
        self.stop_running_build_process()
        self.scan(path=self.build_arguments['root'], relative_path='')
        self.set_option_dependents_and_file_dependents()
        self.execute()
        self.set_watch()

    def parse(self, arguments: List[str]) -> Dict[str, Any]:
        parser = argparse.ArgumentParser(description='Process build options')
        parser.add_argument('options', nargs='*', type=str, help='A list of build options')
        parser.add_argument('--root', type=str, default='\\', help='Root directory where build is to be triggered')
        parser.add_argument('--watch', default='false', type=str, help='Status to run build option on file change')
        parser.add_argument('--poll', type=float, default=1, help='Time interval for checking the file modification status')
        parser.add_argument('--ignore', nargs='*', type=str, help='List of files not to be watched')
        """Breaking the arguments for any '=' attached with key and value"""
        simplified_arguments = list()
        for key_value in arguments:
            for arg in key_value.split('='):
                simplified_arguments.append(arg)
        return vars(parser.parse_args(simplified_arguments))

    def find_path(self, relative_path: str) -> str:
        path: str = relative_path
        if os.path.exists(path):
            return path
        else:
            if path.startswith('~'):
                path = os.getcwd() + path.split('~')[1]
            if os.path.exists(path):
                return path
            else:
                raise BuildAutomationError(f'Invalid relative path: {relative_path}, doesn\'t exists')

    def stop_running_build_process(self) -> None:
        with open(self.PROCESS_FILENAME, 'r') as process_file:
            try:
                process_dict: Any = json.loads(process_file.read())
            except ValueError:
                with open(self.PROCESS_FILENAME, 'w') as process_write_file:
                    process_write_file.write('{}')
                process_dict = json.loads(process_file.read())
            process = self.build_arguments['root']
            if process in process_dict:
                os.system(f'TASKKILL /PID {process_dict[process]} /F')

    def scan(self, path: str, relative_path: str) -> None:
        for filename in os.listdir(path):
            file_path: str = path + filename
            if os.path.isdir(file_path):
                self.scan(path=f'{file_path}\\', relative_path=f'{relative_path}{filename}\\')
            else:
                if filename == self.BUILD_FILENAME:
                    try:
                        json_file: Any = open(file_path)
                        json_dict: Any = json.loads(json_file.read())
                    except ValueError:
                        raise BuildAutomationError(f'Decoding json build configuration file "{file_path}" failed')
                    for properties in json_dict:
                        properties['name'] = os.path.join(relative_path, properties['name'])
                        if properties['name'] not in self.build_options:
                            self.build_options[properties['name']] = Option(properties=properties, command_path=path)
                            if 'deps' not in properties:
                                self.dependency_list[properties['name']] = []
                            else:
                                self.dependency_list[properties['name']] = properties['deps']
                            if 'files' in properties:
                                for files in properties['files']:
                                    filename = os.path.join(path, files)
                                    if filename not in self.build_files:
                                        self.build_files[filename] = File(filename)
                                    self.build_files[filename].dependent_options.append(self.build_options[properties['name']])
                        else:
                            raise BuildAutomationError(f'{properties["name"]} has multifile entities in different build configuration files which conflicts')

    def set_option_dependents_and_file_dependents(self) -> None:
        try:
            graph = Graph(self.dependency_list)
            sorted_dependency: List[str] = graph.depth_first_search()
        except GraphError as e:
            raise BuildAutomationError(e.message)

        """Generating the list of all dependent options for all the options available in build_options"""
        """
        Suppose we have stored the complete dependency for all the direct dependents of a parent option, then
        the complete dependencies of the parent option is the union of dependencies of all the direct dependents.
        We can take the union my marking them in a map which contains options in the order of sorted_dependency(is_dependent in our case)
        the compelete dependencies of the parent option will be the list containing the marked dependencies as they occur in sorted_dependency
        """
        sorted_dependency.reverse()  # the least dependent is kept first
        is_dependent: Dict[Option, bool] = {self.build_options[option_name]: False for option_name in sorted_dependency}
        for option_name in sorted_dependency:
            is_dependent = {key: False for key in is_dependent}
            for direct_dependents in self.dependency_list[option_name]:
                for option in self.build_options[direct_dependents].all_dependent_options:
                    is_dependent[option] = True
            is_dependent[self.build_options[option_name]] = True
            for option in is_dependent:
                if is_dependent[option]:
                    self.build_options[option_name].all_dependent_options.append(option)

        """Creating supporter options list from dependency list -> supporter options are opposite to dependent options"""
        supporter_list: Dict[str, List[str]] = {key: list() for key in self.build_options}
        for option_name in self.dependency_list:
            for dependent in self.dependency_list[option_name]:
                supporter_list[dependent].append(option_name)

        """Generating the list of all supporter options for all the options available in build_options( similar to creating all dependent options)"""
        sorted_dependency.reverse()
        is_supporter: Dict[Option, bool] = {self.build_options[option_name]: False for option_name in sorted_dependency}
        for option_name in sorted_dependency:
            is_supporter = {key: False for key in is_supporter}
            for direct_supporters in supporter_list[option_name]:
                for option in self.build_options[direct_supporters].all_supporter_options:
                    is_supporter[option] = True
            is_supporter[self.build_options[option_name]] = True
            for option in is_supporter:
                if is_supporter[option]:
                    self.build_options[option_name].all_supporter_options.append(option)
        """Generating the list of all dependent options for all the files available in build_files"""
        """It is the union of all supporter options of all the direct dependent options to a file"""
        for files in self.build_files:
            is_supporter = {key: False for key in is_supporter}
            for option in self.build_files[files].dependent_options:
                for supporter_option in option.all_supporter_options:
                    is_supporter[supporter_option] = True
            for option in is_supporter:
                if is_supporter[option]:
                    self.build_files[files].all_dependent_options.append(option)
            self.build_files[files].all_dependent_options.reverse()

    def execute(self) -> None:
        for option in self.build_arguments['options']:
            try:
                self.build_options[option].execute()
            except KeyError:
                raise BuildAutomationError(f'Invalid option "{option}" provided')

    def set_watch(self) -> None:
        ignored_files: List[str] = list()
        if self.build_arguments['ignore']:
            for files in self.build_arguments['ignore']:
                ignored_files.append(self.find_path(files))
            for files in ignored_files:
                print(files)
        if self.build_arguments['watch'].upper() == 'FALSE':
            self.cleanup_running_process()
            return
        elif self.build_arguments['watch'].upper() == 'TRUE':
            self.mark_running_build_process()
            while True:  # To be stopped by giving a command line argument --watch=false with --root being the same directory
                try:
                    sleep(self.build_arguments['poll'])
                    for filename in self.build_files:
                        if filename not in ignored_files:
                            if self.build_files[filename].is_modified():
                                self.build_files[filename].rebuild()
                except KeyboardInterrupt:
                    self.cleanup_running_process()
                    raise BuildAutomationError('The process stopped because of KeyboardInterrupt.')
        else:
            raise BuildAutomationError(f'Invalid argument for watch {self.build_arguments["watch"]}')

    def mark_running_build_process(self) -> None:
        with open(self.PROCESS_FILENAME, 'r') as process_file:
            try:
                process_dict: Any = json.loads(process_file.read())
            except ValueError:
                with open(self.PROCESS_FILENAME, 'w') as process_write_file:
                    process_write_file.write('{}')
                process_dict = json.loads(process_file.read())
            process = self.build_arguments['root']
            process_dict[process] = os.getpid()
            process_json = json.dumps(process_dict)
            with open(self.PROCESS_FILENAME, 'w') as process_write_file:
                process_write_file.write(process_json)

    def cleanup_running_process(self) -> None:
        with open(self.PROCESS_FILENAME, 'r') as process_file:
            try:
                process_dict: Any = json.loads(process_file.read())
            except ValueError:
                with open(self.PROCESS_FILENAME, 'w') as process_write_file:
                    process_write_file.write('{}')
                process_dict = json.loads(process_file.read())
            process = self.build_arguments['root']
            process_dict.pop(process, None)
            process_json = json.dumps(process_dict)
            with open(self.PROCESS_FILENAME, 'w') as process_write_file:
                process_write_file.write(process_json)


if __name__ == '__main__':
    try:
        build = Build(sys.argv[1:])
    except BuildAutomationError as e:
        print(e.message)
