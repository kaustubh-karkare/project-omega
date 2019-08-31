import re
import json

class ValidationError(Exception):
    """Error class"""
    def __init__(self, message):
        self.message = message
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

    def add_mutually_exclusive_options(self, exclusive_options_list):
        """adds conflicting commands to a list as a tuple"""
        self.mutually_exclusive_options.append(exclusive_options_list)

    def parse(self, args):
        """Parses the arguments and makes call to validate them"""
        arguments = {}
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
        self.check_conflicting(arguments)
        return json.dumps(arguments)

    def check_required(self, arguments):
        """To check if any required command is missing"""
        for option in self.options:
            if option.is_required is True:
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
            raise ValidationError("Unknown Command " + command)

    def check_conflicting(self, arguments):
        #check for conflicting commands
        for lists in self.mutually_exclusive_options:
            commands_taken_from_list = []
            for command in lists:
                if command in arguments:
                    commands_taken_from_list.append(command)
            if len(commands_taken_from_list) > 1:
                raise ValidationError('The commands ' + ' '.join(str(conflicting_command)
				for conflicting_command in commands_taken_from_list) + ' cannot be used together')

class Option(object):
    """
    Option -
    option_name - contains the name of command
    option_description - contains its description
    option_type - contains the type of value (string, positiveInteger, etc)
    isRequired - bool value to check if option is required or not
    """
    def __init__(self, option_name, option_description, option_type, is_required):
        self.option_name = option_name
        self.option_description = option_description
        self.option_type = option_type
        self.regex = self.get_regex()
        self.is_required = is_required

    def __str__(self):
        return self.option_name

    def get_regex(self):
        if bool(re.match(self.option_type, 'positive integer', re.IGNORECASE)):
            return r'^[0-9]+$'
        return r'^\w+$'
