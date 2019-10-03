import json
from typing import List


class Command:
    """Stores Command Information"""
    def __init__(self, *, name: str, command_string: str, deps: List[str] = None, files: List[str] = None) -> None:
        self._name = name
        self._command_string = command_string
        self._files = files
        self._dependencies = deps

    def get_name(self) -> str:
        return self._name

    def get_files(self) -> List[str]:
        if self._files is not None:
            return self._files
        raise Command.NoFilesException("No Files for {}".format(self._name))

    def get_command_string(self) -> str:
        return self._command_string

    def get_dependencies(self) -> List[str]:
        if self._dependencies is not None:
            return self._dependencies
        raise Command.NoDependenciesException("No Dependencies for {}".format(self._name))

    class NoDependenciesException(Exception):
        pass

    class NoFilesException(Exception):
        pass


class BuildConfig:
    """Parses and Stores build.config"""
    def __init__(self, json_containing_folder: str) -> None:
        # Parse JSON
        json_path = json_containing_folder + "/build.json"
        with open(json_path) as file_handle:
            self._raw_json = json.load(file_handle)

        self._name_to_command_object = {}
        for command_entry in self._raw_json:
            name = command_entry['name']
            command_string = command_entry['command']
            deps = None
            if 'deps' in command_entry:
                deps = command_entry['deps']
            files = None
            if 'files' in command_entry:
                files = command_entry['files']
            self._name_to_command_object[name] =\
                Command(name=name, command_string=command_string, deps=deps, files=files)

    def get_command(self, command_name: str) -> Command:
        if command_name in self._name_to_command_object:
            return self._name_to_command_object[command_name]
        else:
            raise BuildConfig.UnknownCommandException('No such command "{}" found.'.format(command_name))

    class UnknownCommandException(Exception):
        pass


if __name__ == '__main__':
    pass
