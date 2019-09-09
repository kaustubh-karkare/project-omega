import json


class BuildConfig:
    """Parses and Stores build.config"""
    def __init__(self, json_path):
        # Parse JSON
        json_file = open(json_path)
        self._raw_json = json.load(json_file)
        json_file.close()

        # Validate the config file
        self.validate()

        self._command = {}
        for command in self._raw_json:
            self._command[command['name']] = command

    def command_names(self):
        """Returns list of Commands"""
        return list(self._command)

    def deps(self, command_name):
        """Return List of Dependencies"""
        return self._command[command_name]['deps']

    def command(self, command_name):
        """Returns Command String"""
        return self._command[command_name]['command']

    def files(self, command_name):
        """Returns List of Associated Files"""
        return self._command[command_name]['files']

    def validate(self):
        # TODO: Think about cases and Implement this
        pass


if __name__ == "__main__":
    pass
