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

    def add_argument(self, arg_name, *, required=False, used=False, mutually_exclusive_arg=False, **kwargs):

        self.args[arg_name] = dict()
        self.args[arg_name]["required"] = required
        self.args[arg_name]["used"] = used
        for name, value in kwargs.items():
            self.args[arg_name][name] = value

        if mutually_exclusive_arg:
            self.mutually_exclusive_args.append(arg_name)

    def parse_arguments(self, argv=None):
        """
        Parses argument and assignes value to argument dictionary
        """
        if not argv:
            argv = sys.argv[1:]

        for argument in argv:
            name, sign, value = argument.partition('=')
            name = name.split("-")[-1]
            try:
                value = self.args[name]["type"](value)
            except TypeError:
                pass
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
            if self.args[arg]["used"] and (arg in self.mutually_exclusive_args):
                for other_arg in self.mutually_exclusive_args:
                    if self.args[other_arg]["used"]:
                        raise SimultaneousUsageError(arg, self.mutually_exclusive_args)

        for argument in self.args:      #checking if the required argument is being used or not
            if self.args[argument]["required"]:
                if not self.args[argument]["used"]:
                    raise ReqArgError(argument)

        output_dict = dict()
        for arg in self.args:
            if self.args[arg]["used"]:
                output_dict[arg] = self.args[arg]["value"]
        return output_dict

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
