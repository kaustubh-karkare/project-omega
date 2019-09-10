import sys
import json
import re


class CommandLineParser():

    def __init__(self):
        self.commands = {}

    def add_command(self, command_name, format = None, is_required = False, conflicting_command = None, is_flag = False):
        command = {'command_name': command_name, 'format': format, 'is_required': is_required, 'conflicting_command': conflicting_command, 'is_flag': is_flag}
        self.commands[command_name] = command

    def get_arguments(self, argv):
        results = {}
        commands_found = set()
        flag = False

        for arg in argv[1:]:
            command = None
            value = None
            argument = arg.split('=')

            if len(argument) == 2:
                command, value = argument
            elif len(argument) == 1:
                command = argument[0]
            elif len(argument) > 2:
                raise Exception('invalid number of arguments passed to ' + argument[0])

            commands_found.add(command)

            if command not in self.commands: # commands with at least one argument
                    raise Exception(command + ' is not a recognized command')
            else:
                if self.commands[command]['is_flag'] is True:
                    results[command] = True
                    flag = True
                    continue
                format = self.commands[command]['format']
                if re.fullmatch(format, value):
                    results[command] = value
                else:
                   raise Exception('invalid argument to ' + command)

        for command in commands_found:
            conflicting_command = self.commands[command]['conflicting_command']
            if conflicting_command is not None and conflicting_command in commands_found:
                raise Exception('The ' + command + ' and ' + conflicting_command + ' arguments cannot be used together')

        for command in self.commands:
            instruction = self.commands[command]
            if flag is False and instruction['is_required'] == True and command not in commands_found:
                raise Exception('The ' + command + ' argument is required, but missing from input')
        
        final_response = json.dumps(results, sort_keys=True)
        return {'final_response': final_response}