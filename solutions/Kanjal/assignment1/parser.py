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
        #commands
        self.options = []
        #mutually exclusive commands
        self.mutually_exclusive_options = []

    def __str__(self):
        return ", ".join(str(option) for option in self.options)

    def add_option(self, option_name, option_description, option_type, required):
        """To add a Option object to list of commands"""
        option_being_added = Option(option_name, option_description, option_type, required)
        self.options.append(option_being_added)

    def add_mutually_exclusive_options(self, option1, option2):
        """adds conflicting commands to a list as a tuple"""
        self.mutually_exclusive_options.append((option1, option2))

    def parse(self, args):
        arguments = {}
        """Parses the arguments and makes call to validate them"""
        for arg in args[1:]:
            arg_pair = arg.split('=')
            command = arg_pair[0]
            if len(arg_pair) > 2:
                raise ValidationError("too many arguments")
            if len(arg_pair) == 2:
                value = arg_pair[1]
                self.validate_type_and_existence(command, value)
                arguments[(str(command))] = str(value)
            if len(arg_pair) == 1:
                self.validate_type_and_existence(command, 'True')
                arguments[(str(command))] = 'True'

        self.check_required(arguments)
        return json.dumps(arguments)

    def check_required(self, arguments):
        """To check if any required command is missing"""
        for option in self.options:
            if option.isRequired is True:
                currently_valid = False
                for commands in arguments:
                    if commands == option.option_name:
                        currently_valid = True
                        break
                if currently_valid is False:
                    raise ValidationError("Missing Required Argument "+ option.option_name)

    def validate_type_and_existence(self, command, value):
        """Ensures that command and value are valid"""
        currently_valid = False
        for option in self.options:
            if option.option_name in command:
                currently_valid = True
                if bool(re.match(option.regex, value)):
                    break
                else:
                    raise ValidationError('Expected type '+ option.option_type+' but got '+
				                            str(type(value).__name__) + ' in command '+ command)
                break
        if currently_valid is False:
            raise ValidationError("Command Not Found")

    def check_conflicting(self, arguments):
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
    isRequired - bool value to check if option is required or not
    """
    def __init__(self, option_name, option_description, option_type, isRequired):
        self.option_name = option_name
        self.option_description = option_description
        self.option_type = option_type
        self.regex = self.get_regex()
        self.isRequired = isRequired

    def __str__(self):
        return self.option_name

    def get_regex(self):
        if bool(re.match(self.option_type, 'positive integer', re.IGNORECASE)):
            return r'^[0-9]+$'
        return r'^\w+$'

OPTIONS = Parser()
OPTIONS.add_option('--key', '--key', 'positive Integer', True)
OPTIONS.add_option('--local', 'for local', 'string', False)
OPTIONS.add_option('--remote', 'for local', 'string', False)
OPTIONS.add_option('--name', 'for local', 'string', False)
OPTIONS.add_mutually_exclusive_options('--local', '--remote')
JSON_RETURNED = OPTIONS.parse(sys.argv)
print(JSON_RETURNED)
