from re import search
from sys import stderr


class Parser:

    def __init__(self):
        # print("class created")
        self._expected_args = {}
        self._required_args = {}

    def add_option(self, *args, **kwargs):
        """ Function for adding expected arguments info

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
        for keys, value in self._expected_args.items():
            for i in value:
                if i == 'required':
                    self._required_args[keys] = value

        unique_key_nums = 0
        present_unique_key = ""
        previous_unique_key = ""
        user_passed_args = {}

        for keys in argslist:
            if keys.startswith('--'):
                x = keys[2:].partition('=')
                name = x[0]
                value = x[2]
                if name not in self._expected_args:
                    try:
                        raise ValueError("unexpected")
                    except Exception as error:
                        return str(error)
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        try:
                            if(self.isstring(value) and isinstance(self._expected_args[name]['type'], int) == False):
                                try:
                                    raise ValueError("typeerrorstring")
                                except Exception as error:
                                    return str(error)
                            else:
                                value = str(value)
                        except ValueError:
                            return self.checking
                user_passed_args[name] = value
                typeuserpassed = type(value)
                typeuserdefined = self._expected_args[name]['type']
                if(typeuserdefined != typeuserpassed):
                    self.checking = "typeerror"
                    try:
                        raise TypeError("typeerror")
                    except Exception as error:
                        return str(error)

                if 'unique_key' in self._expected_args[name].keys():
                    previous_unique_key = present_unique_key
                    present_unique_key = self._expected_args[name]['unique_key']
                if previous_unique_key != "" and previous_unique_key != present_unique_key:
                    try:
                        raise ValueError("conflict")
                    except Exception as error:
                        return str(error)

        for commands in self._required_args:
            if commands not in user_passed_args:
                try:
                    raise ValueError("mandatoryerror")
                except Exception as error:
                    return str(error)
        return user_passed_args

    def isstring(self, string):
        """ Function for checking whether a string contains number or not 

        Args:
            string: String to be checked
        Returns
            boolean depending on string
        """
        return bool(search(r'\d', string))
