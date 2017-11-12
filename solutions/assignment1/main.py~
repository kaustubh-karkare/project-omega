import re


class assignment1:

    def __init__(self):
       # print("class created")
        self.copyargs = {}
        self.requiredargs = {}
        self.nonrequiredargs = {}
        self.checking = "noerror"
        self.userpassedargs = {}
        self.userpassrequiredargs = {}
        self.userpassnonrequiredargs = {}
        self.type = ""
        self.local = []

    def createoptions(self, **wargs):
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
                self.requiredargs[commands] = self.copyargs[commands]
            else:
                self.nonrequiredargs[commands] = self.copyargs[commands]
        return wargs

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
            if commands in self.requiredargs:
                self.userpassrequiredargs[commands] = self.userpassedargs[commands]
            else:
                self.userpassnonrequiredargs[commands] = self.userpassedargs[commands]

      #  print(self.userpassnonrequiredargs)
        self.validateargs()

    def validateargs(self):
        """ Function for receiving the list of commands provided by the user and validate it accordingly

        """
        # Checking error for mandatory and non-mandatory
        for commands in self.requiredargs:
            if commands not in self.userpassrequiredargs:
                self.checking = "mandatoryerror"
                self.errorlisting(self.checking, commands)
                exit()
        for commands in self.userpassedargs:
            if commands not in self.copyargs:
                self.checking = "overflow"
                self.errorlisting(self.checking, commands)
                exit()

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
                        if(self.isstring(self.userpassedargs[commands])):
                            self.checking = "typeerrorstring"
                            self.errorlisting(self.checking, commands)

                        else:
                            
                            self.userpassedargs[commands] = str(
                            self.userpassedargs[commands])
                    except ValueError:
                       exit()    
                    
                        
                    

        # Type Checking(datatype checking)
        for commands in self.userpassedargs:
            typeuserpassed = type(self.userpassedargs[commands])
            typeuserdefined = type(self.copyargs[commands][0])
            if(typeuserdefined != typeuserpassed):
                self.checking = "typeerror"
                self.type = typeuserdefined
                self.errorlisting(self.checking, commands)
                exit()
                
                
        for commands in self.userpassedargs:
            self.local.append(self.copyargs[commands][2])
            
        if "local" in self.local and "remote" in self.local:
            self.checking = "conflict"
            self.errorlisting(self.checking,"both")
            exit()
        
        if self.checking == "noerror":
            print(self.userpassedargs)

    def errorlisting(self, errorcategory, command):
        """ Function for generating the list of errors

        """
        print("Error: ")
        if errorcategory == "mandatoryerror":
            print("The \"--%s\" argument is required, but missing from input." % command)
        elif errorcategory == "overflow":
            print("There is no \"--%s\" argument named " % command)
        elif errorcategory == "typeerror":
            print("The value for the \"--%s\" argument must be a of type %s" %
                  (command, self.type.__name__))
        elif errorcategory =="typeerrorstring":
             print("The value for the \"--%s\" argument must be a of type string" %
                  (command))
        elif errorcategory =="conflict":
            print("Conflicting situation found 2 mutually exclusive arguments found")
    
    def isstring(self,string):
         """ Function for checking whether a string contains number or not 
         
         Args:
             string: String to be checked
         Returns
             boolean depending on string
         """
         return bool(re.search(r'\d',string))
         
         

