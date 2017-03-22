"""Exceptions for solution module."""


class DuplicateArgError(Exception):
    def __init__(self, arg_name):
        error_message = "The argument '%s' already exists." % arg_name
        super().__init__(error_message)


class ParsingError(Exception):
    # Superclass for all parsing errors
    def __init__(self, error_message):
        super().__init__(error_message)


class RequiredArgError(ParsingError):
    def __init__(self, arg_name):
        error_message = "The argument '%s' is required." % arg_name
        super().__init__(error_message)


class ExclusiveArgError(ParsingError):
    def __init__(self, arg_names):
        error_message = "%s cannot be used together." % str(arg_names)[1:-1]
        super().__init__(error_message)


class UnknownArgError(ParsingError):
    def __init__(self, arg_name):
        error_message = "The argument '%s' is invalid" % arg_name
        super().__init__(error_message)


class ValueCountError(ParsingError):
    def __init__(self, arg_name):
        error_message = "Too few values supplied for '%s'" % arg_name
        super().__init__(error_message)


class ValueTypeError(ParsingError):
    def __init__(self, arg_name):
        error_message = "Invalid value type(s) for '%s'" + arg_name
        super().__init__(error_message)


class PosargCountError(ParsingError):
    def __init__(self):
        error_message = 'Too many positional arguments (or values).'
        super().__init__(error_message)


class PosargTypeError(ParsingError):
    def __init__(self, arg_name):
        error_message = "Invalid value type for '%s'" % arg_name
        super().__init__(error_message)
