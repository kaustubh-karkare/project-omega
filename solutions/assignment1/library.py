from re import search
from sys import stderr


class ParserError(Exception):

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return(str(self.value))


class Parser:

    def __init__(self):
        # print("class created")
        self._expected_args = {}
        self._required_args = {}

    def add_option(self, *args, **kwargs):
        """ Function for adding expected arguments info
            add_option(name,required=true,type=float,unique_key=local)
        Args:
            **kwargs : Keyword Arguments with expected arguments information
        """
        for arg in args:
            self._expected_args[arg] = kwargs

    def parse(self, argslist):
        """ Function for parsing and validating the commands

        Args:
            argslist : List of commands given by user

        Returns:
            The User passed values if everything goes well , otherwise returns the error
        """
        # Storing required Args for Error Checking
        required_args = set(
            [name for name, value in self._expected_args.items() if "required" in value])

        unique_key_nums = 0
        present_unique_key = ""
        previous_unique_key = ""
        user_passed_args = {}

        for keys in argslist:
            if keys.startswith('--'):
                name, _separator, value = keys[2:].partition('=')
                if name not in self._expected_args:
                    raise ParserError("unexpected")

                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        try:
                            if(self.isstring(value) and isinstance(self._expected_args[name]['type'], int) == False):
                                raise TypeError("typeerrorstring")
                            else:
                                value = str(value)
                        except ValueError:
                            return self.checking
                user_passed_args[name] = value
                typeuserpassed = type(value)
                typeuserdefined = self._expected_args[name]['type']
                if(typeuserdefined != typeuserpassed):
                    self.checking = "typeerror"
                    raise TypeError("typeerror")

                if 'unique_key' in self._expected_args[name].keys():
                    previous_unique_key = present_unique_key
                    present_unique_key = self._expected_args[name]['unique_key']
                if previous_unique_key != "" and previous_unique_key != present_unique_key:
                    raise ParserError("conflict")

        for commands in required_args:
            if commands not in user_passed_args:
                raise ParserError("mandatoryerror")
        return user_passed_args

    def isstring(self, string):
        """ Function for checking whether a string contains number or not 

        Args:
            string: String to be checked
        Returns
            boolean depending on string
        """
        return bool(search(r'\d', string))
