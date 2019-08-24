import sys
Integer, String, Others, Required = set(), set(), set(), set()
errors, Json = dict(), dict()
class Parser:
    """Class for adding the command line arguments, storing errors, storing results and displaying them"""
    def add_argument(self, argument, required, types):
        if types == 'integer':
            Integer.add(argument)
            if required == 'yes':
                Required.add(argument)
        elif types == 'string':
            String.add(argument)
            if required == 'yes':
                Required.add(argument)
        else:
            Others.add(argument)
            if required == 'yes':
                Required.add(argument)
    def store_error(self, key, error):
        errors.setdefault(key, []).append(error)
    def store_result(self, key, value):
        Json[key] = value
    def check_required(self, keys):
        for check in Required:
            flag = False
            for key in keys:
                if key == check:
                    flag = True
            if not flag:
                return False, check
        return True, "ok"
    def display_error(self):
        for key in errors:
            for error in errors[key]:
                if error == "no-value" and key not in ("--local", "--remote"):
                    print("Error: The value for argument '"+key+"' is missing")
                if error == "required":
                    print("Error: The argument '"+key+"' is required, but missing from input")
                if error == "local and remote":
                    print("Error: The '--local' and '--remote' arguments cannot be used together")
                if error == "not-int":
                    print("Error: The value for argument '"+key+"' must be integer")
                if error == "not-string":
                    print("Error: The value for argument '"+key+"' must be string")
                if error == "invalid-argument":
                    print("Error: invalid argument '"+key+"'")
    def display_result(self):
        print('{')
        for key in Json:
            print("'"+key+"' : '"+Json[key]+"',")
        print('}')

def main(argument):
    parse = Parser()
    parse.add_argument('--key', 'yes', 'integer')
    parse.add_argument('--name', 'no', 'string')
    parse.add_argument('--local', 'no', 'others')
    parse.add_argument('--remote', 'no', 'others')
    length_of_arguments = len(argument)
    if length_of_arguments == 1:
        print("Error: no arguments given in input")
        return 0
    check = False
    keys = list()
    for arguments in range(1, length_of_arguments):
        args = argument[arguments]
        key = args.partition('=')[0]
        value = args.partition('=')[2]
        keys.append(key)
        if key not in ("--remote", "--local"):
            parse.store_result(key, value)
            if (key not in Integer) and (key not in String) and(key not in Others):
                parse.store_error(key, "invalid-argument")
            if '=' not in args:
                parse.store_error(key, "no-value")
            if key in Integer:
                if not value.isdigit():
                    parse.store_error(key, "not-int")
            if key in String:
                if not value.isalpha():
                    parse.store_error(key, "not-string")
        if key == '--local' and not check:
            check = True
        elif key == '--remote' and not check:
            check = True
        elif check and key in ('--local', '--remote'):
            parse.store_error(key, "local and remote")
    response, key = parse.check_required(keys)
    if not response:
        parse.store_error(key, "required")
    if bool(errors):
        parse.display_error()
    else:
        parse.display_result()

if __name__ == '__main__':
    main(sys.argv)
    
