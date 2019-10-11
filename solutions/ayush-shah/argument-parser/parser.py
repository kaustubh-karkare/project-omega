import json

class ParseError(Exception):
    """
    Class for raising exceptions
    """
    
    def __init__(self, message):
        super(ParseError, self).__init__(message)

class Options(object):
    """
    Class for storing argument information
    """
    
    def __init__(self, argument, types, required):
        self.argument = argument
        self.types = types
        self.required = required
        
class Parser:
    """
    Class for adding the command line arguments
    storing errors, storing results and displaying them
    """
    
    def __init__(self):
        self.arguments = []
        self.Json = {}

    def add_argument(self, argument, required, types):
        add = Options(argument, types, required)
        self.arguments.append(add)

    def store_result(self, key, value):
        self.Json[key] = value

    def check_required(self, keys):
        for check in self.arguments:
            flag = False
            if check.required == False:
                continue
            for key in keys:
                if key == check.argument and check.required == True:
                    flag = True
            if not flag:
                return False, check.argument
        return True, "ok"

    def check_local_and_remote(self, argument):
        length_of_arguments = len(argument)
        check = False
        for arguments in range(1, length_of_arguments):
            args = argument[arguments]
            key = args.partition('=')[0]
            if key == '--local' and not check:
                check = True
            elif key == '--remote' and not check:
                check = True
            elif check and key in ('--local', '--remote'):
                return True
        return False

    def display_result(self):
        to_json = json.dumps(self.Json)
        return to_json

    def main(self, argument):
        length_of_arguments = len(argument)
        if length_of_arguments == 1:
            raise ParseError("Error: no arguments given in input")
        if self.check_local_and_remote(argument):
            raise ParseError("Error: The '--local' and '--remote' arguments cannot be used together")
        keys = list()
        for arguments in range(1, length_of_arguments):
            args = argument[arguments]
            key = args.partition('=')[0]
            value = args.partition('=')[2]
            keys.append(key)
            if key not in ("--remote", "--local"):
                self.store_result(key, value)
            flag = False
            for obj in self.arguments:
                if obj.argument == key:
                    flag = True;
            if not flag:
                raise ParseError("Error: invalid argument '" + key + "'")
            if '=' not in args:
                raise ParseError("Error: The value for argument '" + key + "' is missing")
            flag = False
            for obj in self.arguments:
                if obj.types == "integer" and obj.argument == key:
                    flag = True;
            if flag:
                if not value.isdigit():
                    raise ParseError("Error: The value for argument '" + key + "' must be integer")
            if not flag:
                if not value.isalpha():
                    raise ParseError("Error: The value for argument '" + key + "' must be string")

        response, key = self.check_required(keys)
        if not response:
            raise ParseError("Error : argument '" + key + "' is required but missing")
        return self.display_result()
