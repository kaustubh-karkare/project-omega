import re
import json
import sys

class ValidationError(Exception):
    """Error class"""
    def __init__(self, message):
        super().__init__(message)

class Parser(object):
    """ Parser """
    def __init__(self):
	#storing conflicting arguments
        self.commands_conflicting = []
	#arguments recieved storage
        self.arguments = []
        #commands
        self.options = []
        #Required commands
        self.required_options = []
        #mutually exclusive commands
        self.mutually_exclusive_options = []

    def __str__(self):
        return ", ".join(str(option) for option in self.options)

    def add_option(self, option_name, option_description, option_type, required):
        """To add a Option object to list of commands"""
        option_being_added = Option(option_name, option_description, option_type)
        self.options.append(option_being_added)
        if required:
            self.required_options.append(option_being_added)

    def add_mutually_exclusive_options(self, option1, option2):
        """adds conflicting commands to a list as a tuple"""
        self.mutually_exclusive_options.append((option1, option2))

    def parse(self, args):
        """Parses the arguments and makes call to validate them"""
        for arg in args[1:]:
            arg_pair = arg.split('=')
            command = arg_pair[0]
            if len(arg_pair) > 2:
                raise ValidationError("too many arguments")
            if len(arg_pair) == 2:
                value = arg_pair[1]
                self.validate(command, value)
                self.arguments.append((str(command), str(value)))
            if len(arg_pair) == 1:
                self.validate(command, 'True')
                self.arguments.append((str(command), 'True'))

        self.check_required()
        return json.dumps(dict(self.arguments))

    def check_required(self):
        """To check if any required command is missing"""
        for option in self.required_options:
            currently_valid = False
            for commands in self.arguments:
                if commands[0] == option.option_name:
                    currently_valid = True
                    break
            if currently_valid is False:
                raise ValidationError("Missing Required Argument "+ option.option_name)

    def validate(self, command, value):
        """Ensures that command and value are valid"""
        currently_valid = False
        for option in self.options:
            if bool(re.match(option.option_name, str(command), re.IGNORECASE)):
                currently_valid = True
                if bool(re.match(option.regex, value)):
                    break
                else:
                    raise ValidationError('Expected type '+ option.option_type+' but got '+
				                            str(type(value).__name__) + ' in command '+ command)
                break
        if currently_valid is False:
            raise ValidationError("Command Not Found")

        #check for conflicting commands
        for conflicting_commands_pair in self.mutually_exclusive_options:
            for possible_conflicts in self.commands_conflicting:
                if command == possible_conflicts[0]:
                    raise ValidationError('The '+ possible_conflicts[1] + ' and ' +
				                            possible_conflicts[0] + ' commands cannot be used together')
            if command == conflicting_commands_pair[0]:
                self.commands_conflicting.append((conflicting_commands_pair[1], command))
            elif command == conflicting_commands_pair[1]:
                self.commands_conflicting.append((conflicting_commands_pair[0], command))

class Option(object):
    """
    Option -
    option_name - contains the name of command
    option_description - contains its description
    option_type - contains the type of value (string, positiveInteger, etc)
    """
    def __init__(self, option_name, option_description, option_type):
        self.option_name = option_name
        self.option_description = option_description
        self.option_type = option_type
        self.regex = self.get_regex()

    def __str__(self):
        return self.option_name

    def get_regex(self):
        if bool(re.match(self.option_type, 'positive integer', re.IGNORECASE)):
            return r'^[0-9]+$'
        return r'^\w+$'

OPTIONS = Parser()
OPTIONS.add_option('--key', '--key', 'positive Integer', 1)
OPTIONS.add_option('--local', 'for local', 'string', 0)
OPTIONS.add_option('--remote', 'for local', 'string', 0)
OPTIONS.add_option('--name', 'for local', 'string', 0)
OPTIONS.add_mutually_exclusive_options('--local', '--remote')
JSON_RETURNED = OPTIONS.parse(sys.argv)
print(JSON_RETURNED)
