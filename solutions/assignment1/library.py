from re import search
from sys import stderr


class store_args_options:

    def __init__(self):
        self._all_args = {}
        self._required_args = {}
        self._non_required_args = {}
        self._user_passed_args = {}
        self._user_pass_req_args = {}
        self._user_pass_nonreq_args = {}

    def add_required_args(self, command, reqargs):
        """ Adding new required args"""
        self._required_args[command] = reqargs

    def add_nonrequired_args(self, command, nonreqargs):
        """ Adding new non required args"""
        self._non_required_args[command] = nonreqargs

    def get_required_args(self):
        """ Return required args"""
        return self._required_args

    def get_non_required_args(self):
        """ Return non-required args """
        return self._non_required_args

    def add_user_required_args(self, command, user_req_args):
        """ Adding new user required args"""
        self._user_pass_req_args[command] = user_req_args

    def add_user_nonrequired_args(self, command, usernonreqargs):
        """ Adding new user non-required args"""
        self._user_pass_nonreq_args[command] = usernonreqargs

    def get_user_require_args(self):
        """ Return UserPassed Required Args"""
        return self._user_pass_req_args

    def get_user_nonrequired_args(self):
        """ Return UserPassed non-required Args"""
        return self._user_pass_nonreq_args

    def add_all_args(self):
        """ Get all the required and non-required args"""
        for x in self._required_args:
            self._all_args[x] = self._required_args[x]
        for y in self._non_required_args:
            self._all_args[y] = self._non_required_args[y]

    def get_all_args(self):
        """ Return all args"""
        return self._all_args


class parser:

    def __init__(self):
        # print("class created")
        self.copyargs = {}
        self.checking = "noerror"
        self.userpassedargs = {}
        self.type = ""
        self.local = []
        self.record = store_args_options()

    def add_options(self, **wargs):
        """ Function for creating the command line options

        Args:
            **wargs : Keyword Arguments (List of Command line options passed)
        Returns:
            A dictionary of containing Command Line Options

        """
        # Making copy of required and nonrequiredargs

        self.copyargs = wargs
        for commands in self.copyargs:
            temp = self.copyargs[commands][1]
            if temp == "r":
                self.record.add_required_args(
                    commands, self.copyargs[commands])
            else:
                self.record.add_nonrequired_args(
                    commands, self.copyargs[commands])
        # return wargs
        self.record.add_all_args()

    def parsecommands(self, argslist):
        """ Function for parsing the commands

        Args:
            argslist : List of commands given by user

        """
        for commands in argslist:
            commands = commands.split("--")
            commands[1] = commands[1].split('=')
            self.userpassedargs[commands[1][0]] = commands[1][1]
        # User passed non required arguments and required argumengs
        for commands in self.userpassedargs:
            if commands in self.record.get_required_args():
                self.record.add_user_required_args(
                    commands, self.userpassedargs[commands])
            else:
                self.record.add_user_nonrequired_args(
                    commands, self.userpassedargs)

        return self.validateargs()

    def validateargs(self):
        """ Function for receiving the list of commands provided by the user and validate it accordingly

        """
        # Checking error for mandatory and non-mandatory

        for commands in self.record.get_required_args():
            if commands not in self.record.get_user_require_args():
                self.checking = "mandatoryerror"
                self.errorlisting(self.checking, commands)
                return self.checking

        for commands in self.userpassedargs:
            if commands not in self.record.get_all_args():
                self.checking = "overflow"
                self.errorlisting(self.checking, commands)
                return self.checking

        # Checking for type for the argument values
        for commands in self.userpassedargs:
            try:
                self.userpassedargs[commands] = int(
                    self.userpassedargs[commands])
            except ValueError:
                try:
                    self.userpassedargs[commands] = float(
                        self.userpassedargs[commands])
                except ValueError:
                    try:
                        if(self.isstring(self.userpassedargs[commands]) and isinstance(self.record.get_all_args()[commands][0], int) == False):

                            self.checking = "typeerrorstring"
                            self.errorlisting(self.checking, commands)

                        else:

                            self.userpassedargs[commands] = str(
                                self.userpassedargs[commands])
                    except ValueError:
                        return self.checking

        # Type Checking(datatype checking)
        for commands in self.userpassedargs:

            typeuserpassed = type(self.userpassedargs[commands])
            typeuserdefined = type(self.record.get_all_args()[commands][0])
            if(typeuserdefined != typeuserpassed):
                self.checking = "typeerror"
                print(self.record.get_all_args()[commands])
                self.type = typeuserdefined
                self.errorlisting(self.checking, commands)
                return self.checking

        for commands in self.userpassedargs:
            self.local.append(self.record.get_all_args()[commands][2])

        if "local" in self.local and "remote" in self.local:
            self.checking = "conflict"
            self.errorlisting(self.checking, "both")
            return self.checking

        if self.checking == "noerror":
            return self.userpassedargs
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
                         (command, self.type.__name__))
        elif errorcategory == "typeerrorstring":
            stderr.write("The value for the \"--%s\" argument must be a of type string" %
                         (command))
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
