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
import os
from typing import List
from Builder.global_constants import GlobalConstants


class BuildRule:
    """Stores Command Information"""
    def __init__(self, *, name: str, command: str, deps: List[str] = [], files: List[str] = []) -> None:
        self._name = name
        self._command = command
        self._files = files
        self._dependencies = deps

    def get_name(self) -> str:
        return self._name

    def get_files(self) -> List[str]:
        return self._files

    def get_command(self) -> str:
        return self._command

    def get_dependencies(self) -> List[str]:
        return self._dependencies

    class NoDependenciesException(Exception):
        pass

    class NoFilesException(Exception):
        pass


class BuildConfig:
    """Parses and Stores build.config in the form of BuildRule objects"""
    @classmethod
    def load_from_build_directory(cls, json_containing_directory: str):
        # Parse JSON
        json_path = os.path.join(json_containing_directory, GlobalConstants.CONFIG_FILE_NAME)
        with open(json_path) as file_handle:
            raw_json_str = file_handle.read()
        return cls(raw_json_str)

    def __init__(self, raw_json_str: str) -> None:
        # Parse JSON
        raw_json = json.loads(raw_json_str)
        self._name_to_build_rule = {}
        for raw_build_rule in raw_json:
            name = raw_build_rule.get('name')
            command = raw_build_rule.get('command')
            deps = raw_build_rule.get('deps', [])
            files = raw_build_rule.get('files', [])
            self._name_to_build_rule[name] =\
                BuildRule(name=name, command=command, deps=deps, files=files)

    def get_build_rule(self, command_name: str) -> BuildRule:
        if command_name in self._name_to_build_rule:
            return self._name_to_build_rule[command_name]
        else:
            raise BuildConfig.UnknownCommandException('No such command "{}" found.'.format(command_name))

    class UnknownCommandException(Exception):
        pass
