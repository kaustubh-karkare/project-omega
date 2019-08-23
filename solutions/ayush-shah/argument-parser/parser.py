import sys
Integer, String, Others, Required = set(), set(), set(), set()
errors, Json = dict(), dict()
class Parser:
    def addArgument(self, argument, required, types):
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
    def storeError(self, key, error):
        errors.setdefault(key, []).append(error)
    def storeResult(self, key, value):
        Json[key] = value
    def checkRequired(self, keys):
        for check in Required:
            flag = False
            for key in keys:
                if key == check:
                    flag = True
            if not flag:
                return False,check
        return True, "ok"
    def displayError(self):
        for key in errors:
            for error in errors[key]:
                if error == "no-value" and not(key == "--local" or key == "--remote"):
                    print("Error: The value for argument '"+key+"' is missing")
                if error == "required":
                    print("Error: The argument'"+key+"' is required, but missing from input")
                if error == "local and remote":
                    print("Error: The --local and --remote arguments cannot be used together")
                if error == "not-int":
                    print("Error: The value for argument '"+key+"' must be integer")
                if error == "not-string":
                    print("Error: The value for argument '"+key+"' must be string")
                if error == "invalid-argument":
                    print("Error: invalid argument "+key)
    def displayResult(self):
        print('{')
        for key in Json:
            print("'"+key+"' : '"+Json[key]+"',")
        print('}')

def main():
    parse = Parser()
    parse.addArgument('--key', 'yes', 'integer')
    parse.addArgument('--name', 'no', 'string')
    parse.addArgument('--local', 'no', 'others')
    parse.addArgument('--remote', 'no', 'others')
    length_of_arguments = len(sys.argv)
    if length_of_arguments == 1:
        print("Error: no arguments given in input")
        return 0
    check = False
    keys = list()
    for arguments in range(1, length_of_arguments):
        args = sys.argv[arguments]
        key = args.partition('=')[0]
        value = args.partition('=')[2]
        keys.append(key)
        if key != "--remote" and key != "--local":
            parse.storeResult(key, value)
            if (key not in Integer) and (key not in String) and(key not in Others):
                parse.storeError(key, "invalid-argument")
            if '=' not in args:
                parse.storeError(key, "no-value")
            if key in Integer:
                if not value.isdigit():
                    parse.storeError(key, "not-int")
            if key in String:
                if not value.isalpha():
                    parse.storeError(key, "not-string")
        if key == '--local' and not check:
            check = True
        elif key == '--remote' and not check:
            check = True
        elif check and (key == '--local' or key == '--remote'):
            parse.storeError(key, "local and remote")
    response, key = parse.checkRequired(keys)
    if not response:
        parse.storeError(key, "required")
    if bool(errors):
        parse.displayError()
    else:
        parse.displayResult()
             
if __name__ == '__main__':
    main()  