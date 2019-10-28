"""
Command Line Parser - parses command line arguments
"""

import sys

class Parser(object):
    """
    Class to handle parsing
    """

    def __init__(self, test=False):
        self.args = {}		#storing arguments as objects as values and their names as keys
        self.test = test

    def add_argument(self, arg_name, **kwargs):
        """
        Initializes Argument class
        """
        self.args[arg_name] = dict()
        self.args[arg_name]["used"] = False
        self.args[arg_name]["cant_be_used_with"] = None
        self.args[arg_name]["required"] = False
		
        for name, value in kwargs.items():
            self.args[arg_name][name] = value
            

    def parse_arguments(self, *args):
        """
        Parses argument and assignes value to argument dictionary
        """
        if self.test:
            arguments = args
        else:
            arguments = sys.argv[1:]

        for argument in arguments:
            name, sign, value = argument.partition('=')
            name = name.split("-")[-1]
            try:
                value = int(value) if (self.args[name]["type"] == int) else value        #typecasting
                value = float(value) if (self.args[name]["type"] == float) else value	   
            except ValueError:
                pass
            if value:                
                if not isinstance(value, self.args[name]["type"]):
                    raise WrongTypeError(type(value), self.args[name]["type"], name)
            if not name in self.args:
                raise NoSuchArgError(name)

            self.args[name]["value"] = value
            self.args[name]["used"] = True

        for arg in self.args:       #checking if an argument can be used with the others
            if self.args[arg]["used"]:
                if self.args[arg]["cant_be_used_with"]:
                    for other_arg in self.args[arg]["cant_be_used_with"]:
                        if self.args[other_arg]["used"]:
                            raise SimultaneousUsageError(arg, self.args[arg]["cant_be_used_with"])

        for argument in self.args:      #checking if the required argument is being used or not
            if self.args[argument]["required"]:
                if not self.args[argument]["used"]:
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
