"""
Command Line Parser - parses command line arguments
"""

import sys

class Parser(object):
    """
    Class to handle parsing
    """

    def __init__(self):
        self.args = dict()
        self.mutually_exclusive_args = list()

    def add_argument(self, arg_name, *, required=False, **kwargs):

        self.args[arg_name] = dict()
        self.args[arg_name]["required"] = required
        for attribute_name, attribute_value in kwargs.items():
            self.args[arg_name][attribute_name] = attribute_value

    def add_mutually_exclusive_args(self, *args):

        self.mutually_exclusive_args.append(args)

    def parse_arguments(self, argv=None):
        """
        Parses argument and assignes value to argument dictionary
        """
        arg_parsed = dict()

        if not argv:
            argv = sys.argv[1:]

        for argument in argv:
            name, sign, value = argument.partition('=')
            name = name.split("-")[-1]
            try:
                value = self.args[name]["type"](value)
            except TypeError:        #to catch None calling as a function error which should be ignored
                pass
            except ValueError:          #the typecasting is being done to convert str to respective types but sometimes the entered value is a wrong type which is later raised by the isinstance function
                pass

            if value:
                if not isinstance(value, self.args[name]["type"]):
                    raise WrongTypeError(type(value), self.args[name]["type"], name)
            if not name in self.args:
                raise NoSuchArgError(name)
            
            arg_parsed[name] = value

        for arg in arg_parsed:       #checking if an argument can be used with the others
            for group in self.mutually_exclusive_args:
                if arg in group:
                    for other_arg in group:
                        if other_arg in arg_parsed:
                            raise SimultaneousUsageError(arg, group)

        for argument in self.args:      #checking if the required argument is being used or not
            if self.args[argument]["required"]:
                if not argument in arg_parsed:
                    raise ReqArgError(argument)

        return arg_parsed


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
