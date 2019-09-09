import json


class BuildConfig:
    def __init__(self, json_path):
        json_file = open(json_path)
        self._raw_json = json.load(json_file)
        json_file.close()
        self.validate()
        self._command = {}
        for command in self._raw_json:
            self._command[command['name']] = command

    def command_names(self):
        return list(self._command)

    def deps(self, command_name):
        return self._command[command_name]['deps']

    def command(self, command_name):
        return self._command[command_name]['command']

    def files(self, command_name):
        return self._command[command_name]['files']

    def validate(self):
        pass


if __name__ == "__main__":
    pass
