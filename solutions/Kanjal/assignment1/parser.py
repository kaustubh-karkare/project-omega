import re
import json
from enum import Enum

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

    def add_mutually_exclusive_options(self, exclusive_options_list, is_one_required):
        """adds conflicting commands to a list as a tuple"""
        self.mutually_exclusive_options.append((exclusive_options_list, is_one_required))

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
                arguments[(str(command))] = str(value)
            if len(arg_pair) == 1:
                arguments[(str(command))] = 'True'

        self.validate_type_and_existence(arguments)
        self.check_required(arguments)
        self.check_conflicting(arguments)
        return json.dumps(arguments)

    def check_required(self, arguments):
        """To check if any required command is missing"""
        for option in self.options:
            if option.is_required is True:
                if not option.name in arguments:
                    raise ValidationError("Missing Required Argument "+ option.name)

    def validate_type_and_existence(self, arguments):
        """Ensures that command and value are valid"""
        options_dict = {x.name: x.option_type.value for x in self.options}
        for command in arguments:
            try:
                if not bool(re.match(Option.get_regex(options_dict[command]), arguments[command])):
                    raise ValidationError('Expected type '+options_dict[command] +' but got '+
				                            str(type(arguments[command]).__name__) + ' in command '+ command)
            except KeyError:
                raise ValidationError("Unknown Command "+ command)

    def check_conflicting(self, arguments):
        """check for conflicting commands"""
        for lists in self.mutually_exclusive_options:
            commands_taken_from_list = []
            for command in lists[0]:
                if command in arguments:
                    commands_taken_from_list.append(command)
            if len(commands_taken_from_list) > 1:
                raise ValidationError('The commands ' + ' '.join(str(conflicting_command)
				for conflicting_command in commands_taken_from_list) + ' cannot be used together')
            if lists[1] is True:
                if len(commands_taken_from_list) < 1:
                    raise ValidationError('Atleast one from the mutually exclusive options '+
				    ' '.join(str(command) for command in lists[0])+ ' required')

class OptionType(Enum):
    STRING = "string"
    POSITIVEINTEGER = "positive integer"

class Option(object):
    """
    Option -
    option_name - contains the name of command
    option_description - contains its description
    option_type - contains the type of value (string, positive integer, etc)
    isRequired - bool value to check if option is required or not
    """
    def __init__(self, name, description, option_type, is_required):
        if not isinstance(option_type, OptionType):
            raise ValidationError('Option Type Should be an instance of OptionType Enum,currently '+
                            ' '.join(str(type) for type in OptionType)+ ' are supported')
        self.name = name
        self.description = description
        self.option_type = option_type
        self.regex = Option.get_regex(self.option_type.value)
        self.is_required = is_required

    def __str__(self):
        return self.option_name

    def get_regex(string):
        if bool(re.match(string, 'positive integer', re.IGNORECASE)):
            return r'^[0-9]+$'
        return r'^\w+$'
