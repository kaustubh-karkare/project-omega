"""
Command Line Parser - parses command line arguments
"""

import sys

class Argument(object):
    """
    Class to define argument definitions and characteristics
    """

    def __init__(self, arg_name, arg_type, cant_be_used_with=[], required=False):
        self.arg_name = arg_name
        self.arg_type = arg_type
        self.value = None
        self.required = required
        self.used = False           #flag to identify if the argument is used or not
        self.cant_be_used_with = cant_be_used_with

class Parser(object):
    """
    Class to handle parsing
    """

    def __init__(self):
        self.args = {}          #storing arguments as objects as values and their names as keys

    def add_argument(self, arg_name, arg_type, cant_be_used_with=[], required=False):
        """
        Initializes Argument class
        """
        self.args[arg_name] = Argument(arg_name, arg_type, cant_be_used_with, required)


    def parse_arguments(self):
        """
        Parses argument and assignes value to argument dictionary
        """
        arguments = sys.argv[1:]

        for argument in arguments:
            try:
                arg, value = argument.split('=')
                value = int(value) if value.isdigit() else value        #typecasting integer value if string
            except ValueError:
                arg = argument
                value = None
            arg = arg[2:]           #removing the dashes

            if value:
                if not arg in self.args:
                    raise NoSuchArgError(arg)
                if not isinstance(value, self.args[arg].arg_type):
                    raise WrongTypeError(type(value), self.args[arg].arg_type, arg)
            else:
                if not arg in self.args:
                    raise NoSuchArgError(arg)

            self.args[arg].value = value
            self.args[arg].used = True

        for arg in self.args:       #checking if an argument can be used with the others
            if self.args[arg].used:
                for other_arg in self.args[arg].cant_be_used_with:
                    if self.args[other_arg].used:
                        raise SimultaneousUsageError(arg, self.args[arg].cant_be_used_with)

        for argument in self.args:      #checking if the required argument is being used or not
            if self.args[argument].required:
                if not self.args[argument].used:
                    raise ReqArgError(argument)

class NoSuchArgError(Exception):

    def __init__(self, arg):
        self.message = 'Error: No \'%s\' argument declared.' % arg

    def __str__(self):
        return self.message

class ReqArgError(Exception):

    def __init__(self, arg):
        self.message = 'Error: The \'%s\'  argument is required but missing from the input.' % arg

    def __str__(self):
        return self.message

class SimultaneousUsageError(Exception):

    def __init__(self, arg, cantbeusedwith_arg):
        self.message = ('%s cannot be used with these arguments: %s' % (arg, cantbeusedwith_arg))

    def __str__(self):
        return self.message

class WrongTypeError(TypeError):

    def __init__(self, type_input, type_arg, arg):
        self.message = ('%s type argument added instead of %s for %s' % (type_input.__name__, type_arg.__name__, arg))

    def __str__(self):
        return self.message
