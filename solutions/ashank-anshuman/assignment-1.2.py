from sys import argv
import re

group = []
arguments = {}
shortnotation = {}
comp_args = []

def add_argument(argname,short_argname=None,datatype=str,value=False):
    # Add an argument
    # Keyword arguments:
    # argname -- The name of the argument
    # short_argname -- Short notation of argument (default None)
    # datatype -- Type of data for value of argument (default str)
    # value -- Value required or not (default False)
    
    if type(datatype) is not type and datatype is not None:
        print("Argument 'datatype' incorrect.")
        return
    if type(value) is not bool:
        print("Argument 'value' incorrect.")
        return
    arguments[str(argname).lower()] = {}
    if short_argname:
        arguments[str(argname)]["short_argname"] = str(short_argname).lower()
        shortnotation[str(short_argname).lower()] = str(argname).lower()
    if datatype is None and value is True:
        arguments[str(argname).lower()]["type"] = str
    elif value is True:
        arguments[str(argname).lower()]["type"] = datatype
    arguments[str(argname).lower()]["value"] = value


def group_args(*args):
    # Add conflicting arguments to a common group
    group.append([])
    for arg in args:
        group[len(group)-1].append(arg)

def add_compargs(*args):
    # Add arguments which must be present
    for arg in args:
        comp_args.append(arg)
    

def show_help():
    # Shows usage
    print("Usage : ", end = "")
    for args in arguments:
        if args in comp_args:
            print(args, end = "  ")
        else:
            print("["+args+"]", end = "  ")
    print()

add_argument("--help","-h",None,False)

def parser():
    counter = 0            
    json_output = {}
    for i in range(1,len(argv)):
        arg = argv[i].split('=')
        if arg[0].lower() in arguments or arg[0].lower() in shortnotation:         # Checks if argument exists
            if arg[0].lower() == "--help" or arg[0].lower() == "-h":               # Shows help
                show_help()
                exit(0)
            if arg[0].lower() in shortnotation:                                    # Gets name of shortnotation
                arg[0] = shortnotation[arg[0].lower()]
            if arguments[arg[0]]["value"] is True:
                if len(arg) == 2:
                    if "type" in arguments[arg[0]]:                                  # Checks if value type of argument is correct
                        try:
                            temp = arguments[arg[0]]["type"](arg[1])
                        except:
                            print("Error: command '",arg[0],"' must have a ",
                                   str(arguments[arg[0]]["type"])," argument.")
                            exit(0)
                        if temp is None or bool(temp) is False:
                            print("Error: command '",arg[0],"' must have a ",
                                   str(arguments[arg[0]]["type"])," argument.")
                            exit(0)
                else:
                    print ("Error: argument '",arg[0],"' is missing its value.")
                    exit(0)
                json_output[arg[0]] = arg[1]
            else:
                if len(arg) == 2:
                    print("Error: argument '",arg[0],"' does not require any value.")
                    exit(0)
                if arg[0][0] == '-':                                                 # Adds argument to json type object (dictionary in this case)
                    json_output[arg[0]] = "True"
                else:
                    json_output["sub"*counter+"command"] = arg[0]
                    counter += 1
                
        else:
            print("Error: argument '",arg[0],"' not found.")
            exit(0)

    for arg in comp_args:                                                               # Checks for presence of required arguments
        if arg not in json_output:
            print("Error: '",arg,"' argument is required, but missing from input.")
            exit(0)

    for g in group:                                                                     # Checks if conflicting arguments are present
        count = 0
        temp_list = []
        for arg in json_output:
            if arg in g:
                temp_list.append(arg)
                count += 1
            if count > 1:
                print("Error: arguments '",temp_list[0],"' and '",
                       temp_list[1],"' cannot be used together.")
                exit(0)

    for arg in json_output:                                                             # Formats argument name for returing as json type
        temp = re.sub('[-]', '', arg)
        json_output[temp] = json_output.pop(arg)

    print(json_output)

if __name__ == '__main__':

    # Test Arguments
    add_argument("--key",None,int,True)
    add_argument("--name",None,None,True)
    add_argument("--verbrose","-v",None,False)
    add_argument("alpha",None,None,False)
    add_argument("beta",None,None,False)
    add_argument("--local",None,None,False)
    add_argument("--remote",None,None,False)
    group_args("--local","--remote")

    # Compulsory arguments
    add_compargs("--key","--name")
    
    parser()
