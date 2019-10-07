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

        for key in argslist:
            if key.startswith('--'):
                name, _separator, value = key[2:].partition('=')
                if name not in self._expected_args:
                    raise ParserError("unexpected value", name)

                typeuserdefined = self._expected_args[name]['type']
                if typeuserdefined == int:
                    try:
                        value = int(value)
                    except ValueError:
                        raise ParserError("typeerror")
                if typeuserdefined == float:
                    try:
                        value = float(value)
                    except ValueError:
                        raise ParserError("typeerror")
                typeuserpassed = type(value)
                user_passed_args[name] = value

                if(typeuserdefined != typeuserpassed):
                    self.checking = "typeerror"
                    raise ParserError("typeerror")

                if 'unique_key' in self._expected_args[name].keys():
                    previous_unique_key = present_unique_key
                    present_unique_key = self._expected_args[name]['unique_key']
                if previous_unique_key != "" and previous_unique_key != present_unique_key:
                    raise ParserError("conflict")
            else:
                raise ParserError("Unexpected Format")
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
