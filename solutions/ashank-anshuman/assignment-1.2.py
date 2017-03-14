from sys import argv
import re

group = []
arguments = {}
shortnotation = {}
comp_args = []


def add_argument(*args, **kwargs):
    # Format (arg name,short name(if any),type = int(if required),value = True(if required))
    # Example : add_argument("--key",type = int,value = True)
    # Creates a new argument
    arguments[str(args[0]).lower()] = {}
    arguments[str(args[0])]["value"]=False
    if(len(args)==2):
        arguments[str(args[0])]["arg_shortname"] = str(args[1].lower())
        shortnotation[str(args[1].lower())] = str(args[0]).lower() 
    for k,v in kwargs.items():
        if(k == 'type'):
            arguments[str(args[0])][type] = v
        elif(k == "value"):
            arguments[str(args[0])]["value"] = v


def group_args(*args):
    # Add conflicting arguments to common group
    group.append([])
    for arg in args:
        group[len(group)-1].append(arg)

def add_compargs(*args):
    # Add arguments which must be present
    for arg in args:
        comp_args.append(arg)
    

def show_help():
    # Shows usage
    print ("Usage : ",end="")
    for args in arguments:
        if (args in comp_args):
            print(args, end="  ")
        else:
            print ("["+args+"]" , end="  ")
    print()

add_argument("--help","-h")

def parser():

    # Test Arguments
    add_argument("--key",type = int,value = True)
    add_argument("--name",value = True)
    add_argument("--verbrose","-v")
    add_argument("alpha")
    add_argument("beta")
    add_argument("--local")
    add_argument("--remote")
    group_args("--local","--remote")

    # Compulsory arguments
    add_compargs("--key","--name")

    counter = 0            
    json_output = {}
    for args in argv:
        if(args != "assignment-1.2.py"):
            arg = args.split('=')
            if(arg[0].lower() in arguments or arg[0].lower() in shortnotation):         # Check if argument exists
                if(arg[0].lower()=="--help" or arg[0].lower()=="-h"):                   # Shows help
                    show_help()
                    exit(0)
                if(arg[0].lower() in shortnotation):                                    # Gets name of shortnotation
                    arg[0] = shortnotation[arg[0].lower()]
                if(arguments[arg[0]]["value"]):
                    if(len(arg)==2):
                        if(type in arguments[arg[0]]):                                  # Checks if value type of argument is correct
                            try:
                                temp = arguments[arg[0]][type](arg[1])
                            except:
                                print ("Error: command '",arg[0],"' must have a ",
                                       str(arguments[arg[0]][type])," argument.")
                                exit(0)
                    else:
                        print ("Error: argument '",arg[0],"' is missing its value.")
                        exit(0)
                    json_output[arg[0]] = arg[1]
                else:
                    if(len(arg)==2):
                        print ("Error: argument '",arg[0],"' does not require any value.")
                        exit(0)
                    if(arg[0][0]=='-'):                                                 # Adds argument to json type object (dictionary in this case)
                        json_output[arg[0]] = "True"
                    else:
                        json_output["sub"*counter+"command"] = arg[0]
                        counter += 1
                    
            else:
                print ("Error: argument '",arg[0],"' not found.")
                exit(0)

    for arg in comp_args:                                                               # Checks for presence of required arguments
        if(arg not in json_output):
            print("Error: '",arg,"' argument is required, but missing from input.")
            exit(0)

    for g in group:                                                                     # Checks if conflicting arguments are present
        count = 0
        temp_list = []
        for arg in json_output:
            if(arg in g):
                temp_list.append(arg)
                count += 1
            if(count>1):
                print ("Error: arguments '",temp_list[0],"' and '",
                       temp_list[1],"' cannot be used together.")
                exit(0)

    for arg in json_output:                                                             # Formats argument name for returing as json type
        temp = re.sub('[-]', '', arg)
        json_output[temp] = json_output.pop(arg)

    print (json_output)

if __name__ == '__main__':
    parser()
