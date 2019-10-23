from re import search
from sys import stderr


class ParserError(Exception):

    # Constructor or Initializer
    def __init__(self, value, detail=""):
        self.value = value + " " + detail

    # __str__ is to print() the value
    def __str__(self):
        return(str(self.value))


class Parser:

    def __init__(self):
        # print("class created")
        self._expected_args = {}

    def add_option(self, name, *, required=False, type=str, unique_key=None):
        """ Function for adding expected arguments info
        Args:
            required : Mark it true if any argument is true
            type : type for the argument passed 
            unique_key : unique_key value for no mutually exclusive things
        """
        user_passed_arg = {
            "required": required,
            "type": type,
            "unique_key": unique_key
        }
        self._expected_args[name] = user_passed_arg

    def parse(self, argslist):
        """ Function for parsing and validating the commands

        Args:
            argslist : List of commands given by user

        Returns:
            The User passed values if everything goes well , otherwise returns the error
        """
        # Storing required Args for Error Checking
        required_args = set(
            [name for name, value in self._expected_args.items() for x1, x2 in value.items() if x2 == True])

        unique_key_nums = 0
        present_unique_key = ""
        previous_unique_key = ""
        user_passed_args = {}
        conflict_checker = {}
        uniquekey_count = 0

        for key in argslist:
            if key.startswith('--'):
                name, _separator, value = key[2:].partition('=')
                if name not in self._expected_args:
                    raise ParserError("unexpected value", name)

                try:
                    value = self._expected_args[name]['type'](value)
                except ValueError:
                    raise ParserError("typeerror")
                user_passed_args[name] = value

                uniquekey = self._expected_args[name]['unique_key']

                if uniquekey is not None:
                    if uniquekey in conflict_checker:
                        conflict_checker[uniquekey] = 2
                    else:
                        conflict_checker[uniquekey] = 1
                        uniquekey_count = uniquekey_count + 1

                if uniquekey_count > 1:
                    raise ParserError("conflict")
            else:
                raise ParserError("Unexpected Format")

        for commands in required_args:
            if commands not in user_passed_args:
                raise ParserError("mandatoryerror")
        return user_passed_args
