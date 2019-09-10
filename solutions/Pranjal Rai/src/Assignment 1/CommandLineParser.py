import sys
import json
import re


class CommandLineParser():

    def __init__(self):
        self.commands = []

    def add_command(self, command_name, format = None, required_command = None, conflicting_command = None, is_flag = False):
        command = {'command_name': command_name, 'format': format, 'required_command': required_command, 'conflicting_command': conflicting_command, 'is_flag': is_flag}
        self.commands.append(command)

    def search_command(self, name_of_command):
        for command in self.commands:
            if command['command_name'] == name_of_command:
                    return command
        return None

    def get_arguments(self, argv):
        results = {}
        commands_found = []
        error_message = None

        for arg in argv[1:]:
            command = None
            value = None
            argument = arg.split('=')

            if len(argument) == 2:
                command, value = argument
            elif len(argument) == 1:
                command = argument[0]
            elif len(argument) > 2:
                error_message = 'invalid number of arguments passed to ' + argument[0]

            commands_found.append(command)

            instruction = self.search_command(command)

            if instruction is None: # commands with at least one argument
                try:
                    raise Exception(command + ' is not a recognized command')
                except Exception as exception:
                    return exception
            else:
                if instruction['is_flag'] is True:
                    results[command] = True
                    continue
                format = instruction['format']
                if re.fullmatch(format, value):
                    results[command] = value
                else:
                    try:
                        raise Exception('invalid argument to ' + command)
                    except Exception as exception:
                        return exception

        for command in commands_found:
            instruction = self.search_command(command)
            conflicting_command = instruction['conflicting_command']
            if conflicting_command is not None and conflicting_command in commands_found:
                try:
                    raise Exception('The ' + command + ' and ' + conflicting_command + ' arguments cannot be used together')
                except Exception as exception:
                    return exception

            required_command = instruction['required_command']
            if required_command is not None and required_command not in commands_found:
                try:
                    raise Exception('The ' + required_command + ' argument is required, but missing from input')
                except Exception as exception:
                    return exception
        
        final_response = json.dumps(results, sort_keys=True)
        return final_response