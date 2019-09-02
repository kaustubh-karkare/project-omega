import sys
import json
import re


class AddCommand:
    COMMANDS = {}

    def __init__(self, command_name, command_type, regular_expression, required_command, conflicting_command, is_local):
        self.command_name = command_name
        self.command_type = command_type
        self.regular_expression = regular_expression
        self.required_command = required_command
        self.conflicting_command = conflicting_command
        self.is_local = is_local
        self.COMMANDS[self.command_name] = self


class CommandLineParser(AddCommand):

    def __init__(self):
        self.COMMANDS = super().COMMANDS

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

            if command not in self.COMMANDS: # commands with at least one argument
                error_message = command + ' is not a recognized command'
            else:
                if self.COMMANDS[command].is_local is True:
                    results[command] = True
                    continue
                regular_expression = self.COMMANDS[command].regular_expression
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
                conflicting_command = self.COMMANDS[command].conflicting_command
                if conflicting_command is not None and conflicting_command in commands_found:
                    error_message = 'The ' + command + ' and ' + conflicting_command + ' arguments cannot be used together'
                required_command = self.COMMANDS[command].required_command
                if required_command is not None and required_command not in commands_found:
                    error_message = 'The ' + required_command + ' argument is required, but missing from input'

        final_response = error_message
        if error_message is None:
            final_response = json.dumps(results, sort_keys=True)
        print(final_response)
        return final_response


KEY_COMMAND = AddCommand('--key', 'positive integer', r'\d+', None, None, False)
NAME_COMMAND = AddCommand('--name', 'albhapets only', r'[a-zA-Z]+', '--key', None, False)
LOCAL_COMMAND = AddCommand('--local', None, r'/\A\z/', None, '--remote', True)
REMOTE_COMMAND = AddCommand('--remote', None, r'/\A\z/', None, '--local', True)


if __name__ == '__main__':
    CommandLineParser().get_arguments(sys.argv)
