from re import search
from sys import stderr


class StoreArgsOptions:

    def __init__(self):
        self.user_passed_args = {}

    def add_user_passed_arg(self, key, user_passed_args):
        self.user_passed_args[key] = user_passed_args

    def get_user_passed_arg(self):
        return self.user_passed_args

    def empty_user_passed_arg(self):
        self.user_passed_args = {}


class Parser:

    def __init__(self):
        # print("class created")
        self._expected_args = {}
        self._required_args = {}
        self.checking = "noerror"
        self.type = ""
        self.modes = []
        self.record = StoreArgsOptions()

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
        for key, value in self._expected_args.items():
            for i in value:
                if i == 'required':
                    self._required_args[key] = value

        for keys in argslist:
            keys = keys.split("--")
            keys[1] = keys[1].split('=')
            self.record.add_user_passed_arg(keys[1][0], keys[1][1])

        # Checking error for mandatory and non-mandatory

        for commands in self._required_args:
            if commands not in self.record.get_user_passed_arg():
                print(self.record.get_user_passed_arg())
                self.checking = "mandatoryerror"
                self.errorlisting(self.checking, commands)
                return self.checking

        for commands in self.record.get_user_passed_arg():
            if commands not in self._expected_args:
                self.checking = "overflow"
                self.errorlisting(self.checking, commands)
                return self.checking

        for commands in self.record.get_user_passed_arg():
            try:
                self.record.get_user_passed_arg()[commands] = int(
                    self.record.get_user_passed_arg()[commands])
            except ValueError:
                try:
                    self.record.get_user_passed_arg()[commands] = float(
                        self.record.get_user_passed_arg()[commands])
                except ValueError:
                    try:
                        if(self.isstring(self.record.get_user_passed_arg()[commands]) and isinstance(self._expected_args[commands]['type'], int) == False):

                            self.checking = "typeerrorstring"
                            print(self._expected_args[commands]['type'])
                            self.errorlisting(self.checking, commands)
                            return self.checking
                        else:

                            self.record.get_user_passed_arg()[commands] = str(
                                self.record.get_user_passed_arg()[commands])
                    except ValueError:
                        return self.checking

        # Type Checking(datatype checking)
        for commands in self.record.get_user_passed_arg():

            typeuserpassed = type(self.record.get_user_passed_arg()[commands])
            typeuserdefined = self._expected_args[commands]['type']
            if(typeuserdefined != typeuserpassed):
                self.checking = "typeerror"
                self.type = typeuserdefined
                self.errorlisting(self.checking, commands)
                return self.checking

        for commands in self.record.get_user_passed_arg():
            self.modes.append(self._expected_args[commands]['mode'])

        if "local" in self.modes and "remote" in self.modes:
            self.checking = "conflict"
            self.errorlisting(self.checking, "both")
            return self.checking

        if self.checking == "noerror":
            user_passed_args = self.record.get_user_passed_arg()
            self.record.empty_user_passed_arg()
            return user_passed_args
        else:
            return self.checking

    def errorlisting(self, errorcategory, command):
        """ Function for generating the list of errors

        """

        print("Error: ")
        if errorcategory == "mandatoryerror":
            stderr.write(
                "The \"--%s\" argument is required, but missing from input." % command)
        elif errorcategory == "overflow":
            stderr.write("There is no \"--%s\" argument named " % command)
        elif errorcategory == "typeerror":
            stderr.write("The value for the \"--%s\" argument must be a of type %s" %
                         (command, self._expected_args[command]['type']))
        elif errorcategory == "typeerrorstring":
            stderr.write("The value for the \"--%s\" argument must be a of type %s" %
                         (command, self._expected_args[command]['type']))
        elif errorcategory == "conflict":
            stderr.write(
                "Conflicting situation found 2 mutually exclusive arguments found")

    def isstring(self, string):
        """ Function for checking whether a string contains number or not 

        Args:
            string: String to be checked
        Returns
            boolean depending on string
        """
        return bool(search(r'\d', string))
