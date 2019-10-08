"""" Sample build.json
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
    "command": "g++ algorithms/sort_bubble.o algorithms/sort_merge.o ..."
  }
]
"""

import json
from typing import List
from Builder.global_constants import GlobalConstants


class BuildRule:
    """Stores Command Information"""
    def __init__(self, *, name: str, command_string: str, deps: List[str] = [], files: List[str] = []) -> None:
        self._name = name
        self._command_string = command_string
        self._files = files
        self._dependencies = deps

    def get_name(self) -> str:
        return self._name

    def get_files(self) -> List[str]:
        return self._files

    def get_command_string(self) -> str:
        return self._command_string

    def get_dependencies(self) -> List[str]:
        return self._dependencies

    class NoDependenciesException(Exception):
        pass

    class NoFilesException(Exception):
        pass


class BuildConfig:
    """Parses and Stores build.config in the form of BuildRule objects"""
    def __init__(self, json_containing_folder: str) -> None:
        # Parse JSON
        json_path = json_containing_folder + "/" + GlobalConstants.CONFIG_FILE_NAME
        with open(json_path) as file_handle:
            self._raw_json = json.load(file_handle)

        self._name_to_command_object = {}
        for command_entry in self._raw_json:
            name = command_entry['name']
            command_string = command_entry['command']
            if 'deps' in command_entry:
                deps = command_entry['deps']
            else:
                deps = []
            if 'files' in command_entry:
                files = command_entry['files']
            else:
                files = []
            self._name_to_command_object[name] =\
                BuildRule(name=name, command_string=command_string, deps=deps, files=files)

    def get_command(self, command_name: str) -> BuildRule:
        if command_name in self._name_to_command_object:
            return self._name_to_command_object[command_name]
        else:
            raise BuildConfig.UnknownCommandException('No such command "{}" found.'.format(command_name))

    class UnknownCommandException(Exception):
        pass
