import sys
import json
import re


class AddCommand:

    def __init__(self, command_name, command_type, regular_expression, required_command, conflicting_command, is_flag, commands):
        self.command_name = command_name
        self.command_type = command_type
        self.regular_expression = regular_expression
        self.required_command = required_command
        self.conflicting_command = conflicting_command
        self.is_flag = is_flag
        commands[self.command_name] = self


class CommandLineParser():

    def __init__(self, commands):
        self.commands = commands

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

            if command not in self.commands: # commands with at least one argument
                error_message = command + ' is not a recognized command'
            else:
                if self.commands[command].is_flag is True:
                    results[command] = True
                    continue
                regular_expression = self.commands[command].regular_expression
                if re.fullmatch(regular_expression, value):
                    results[command] = value
                else:
                    error_message = 'invalid argument to ' + command
            
            if error_message:
                break

        if error_message is not None:
            """some error occurred already"""
            pass
        else:
            for command in commands_found:
                conflicting_command = self.commands[command].conflicting_command
                if conflicting_command is not None and conflicting_command in commands_found:
                    error_message = 'The ' + command + ' and ' + conflicting_command + ' arguments cannot be used together'
                required_command = self.commands[command].required_command
                if required_command is not None and required_command not in commands_found:
                    error_message = 'The ' + required_command + ' argument is required, but missing from input'

        final_response = error_message
        
        if error_message is None: # return json object if everything goes fine
            final_response = json.dumps(results, sort_keys=True)
            print(final_response)
            return final_response
        else: # raise an exception if some error occurred
            try:
                raise Exception(final_response)
            except Exception as exception:
                print(exception)
                return exception
            finally:
                pass