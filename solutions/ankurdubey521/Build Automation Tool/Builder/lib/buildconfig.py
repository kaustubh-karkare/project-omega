import json


class BuildConfig:
    """Parses and Stores build.config"""
    def __init__(self, json_containing_folder):
        # Parse JSON
        json_path = json_containing_folder + "/build.json"
        with open(json_path) as file_handle:
            self._raw_json = json.load(file_handle)

        # Validate the config file
        self.get_validate()

        self._name_to_command = {}
        for command in self._raw_json:
            self._name_to_command[command['name']] = command

    def get_command_names(self):
        """Returns list of Commands"""
        return list(self._name_to_command)

    def get_deps(self, command_name):
        """Return List of Dependencies"""
        return self._name_to_command[command_name]['deps']

    def get_command(self, command_name):
        """Returns Command String"""
        return self._name_to_command[command_name]['command']

    def get_files(self, command_name):
        """Returns List of Associated Files"""
        return self._name_to_command[command_name]['files']

    def get_validate(self):
        # TODO: Think about cases and Implement this
        pass


if __name__ == "__main__":
    pass
