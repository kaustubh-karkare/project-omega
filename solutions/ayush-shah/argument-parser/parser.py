import json

class Parser:
    """
    Class for adding the command line arguments
    storing errors, storing results and displaying them
    """
    Integer, String, Others, Required = set(), set(), set(), set()
    Json = dict()

    def add_argument(self, argument, required, types):
        if types == 'integer':
            self.Integer.add(argument)
            if required == 'yes':
                self.Required.add(argument)
        elif types == 'string':
            self.String.add(argument)
            if required == 'yes':
                self.Required.add(argument)
        else:
            self.Others.add(argument)
            if required == 'yes':
                self.Required.add(argument)

    def store_result(self, key, value):
        self.Json[key] = value

    def check_required(self, keys):
        for check in self.Required:
            flag = False
            for key in keys:
                if key == check:
                    flag = True
            if not flag:
                return False, check
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
            return "Error: no arguments given in input"
        if self.check_local_and_remote(argument):
            return "Error: The '--local' and '--remote' arguments cannot be used together"
        keys = list()
        for arguments in range(1, length_of_arguments):
            args = argument[arguments]
            key = args.partition('=')[0]
            value = args.partition('=')[2]
            keys.append(key)
            if key not in ("--remote", "--local"):
                self.store_result(key, value)
            if (key not in self.Integer) and (key not in self.String) and(key not in self.Others):
                return "Error: invalid argument '" + key + "'"
            if '=' not in args:
                return "Error: The value for argument '" + key + "' is missing"
            if key in self.Integer:
                if not value.isdigit():
                    return "Error: The value for argument '" + key + "' must be integer"
            if key in self.String:
                if not value.isalpha():
                    return "Error: The value for argument '" + key + "' must be string"

        response, key = self.check_required(keys)
        if not response:
            return "Error : argument '" + key + "' is required but missing"
        return self.display_result()

