import json


class Command:
    """Stores Command Information"""
    def __init__(self, *, name, command_string, deps=None, files=None):
        self._name = name
        self._command_string = command_string
        if files is None:
            self._hasFiles = False
        else:
            self._hasFiles = True
            self._files = files
        if deps is None:
            self._hasDependencies = False
        else:
            self._hasDependencies = True
            self._dependencies = deps

    def get_name(self):
        return self._name

    def get_files(self):
        if self._hasFiles:
            return self._files
        raise Command.NoFilesException("No Files for {}".format(self._name))

    def get_command_string(self):
        return self._command_string

    def get_dependencies(self):
        if self._hasDependencies:
            return self._dependencies
        raise Command.NoDependenciesException("No Dependencies for {}".format(self._name))

    class NoDependenciesException(Exception):
        pass

    class NoFilesException(Exception):
        pass


class BuildConfig:
    """Parses and Stores build.config"""
    def __init__(self, json_containing_folder):
        # Parse JSON
        json_path = json_containing_folder + "/build.json"
        with open(json_path) as file_handle:
            self._raw_json = json.load(file_handle)

        self._name_to_command = {}
        for command in self._raw_json:
            self._name_to_command[command['name']] = command

    def get_command(self, command_name):
        if command_name in self._name_to_command:
            entry = self._name_to_command[command_name]
            name = entry['name']
            command_string = entry['command']
            deps = None
            if 'deps' in entry:
                deps = entry['deps']
            files = None
            if 'files' in entry:
                files = entry['files']
            return Command(name=name, command_string=command_string, deps=deps, files=files)
        else:
            raise BuildConfig.UnknownCommandException('No such command "{}" found.'.format(command_name))

    class UnknownCommandException(Exception):
        pass


if __name__ == '__main__':
    pass
