""" This module provides interface to add argument and print them along with their value as JSON"""
import sys
import json

String, Integer, required, optional = set(), set(), set(), set()
Alpha_num, Input, ambig = set(), set(), set()
error, json, arg_detail = dict(), dict(), dict()

class Parser:
    """ class to deal with argument parsing"""

    def add_argument(self, name, **kwargs):
        """method to add new argument to framework"""
        for key in kwargs:                                          #iterating over all parameters
            value = kwargs[key]
            if key == "Type":
                if value == "integer":                               #storing key in resepective set
                    Integer.add(name)
                elif value == "string":
                    String.add(name)
                elif value == "alpha_num":
                    Alpha_num.add(name)
                else:
                    ambig.add(name)
            if key == "mandatory" and value == "True":
                required.add(value)
            else:
                optional.add(value)

            arg_detail.setdefault(name, []).append(value)

    def error_store(self, error_type, key):
        """function to store errors"""
        error.setdefault(error_type, []).append(key)

    def key_store(self, key, value):
        """function to add new value to an argument"""
        json.setdefault(key[2:], []).append(value)

    def error_display(self):
        """function to display the errors to user"""
        for error_type in error:
            for arg in error[error_type]:
                if error_type == "no_input":
                    print "Error :value for '"+arg+"'argument is empty."
                if error_type == "not_support":
                    print "Error :argument '"+arg+"'is not supported."
                if error_type == "not_int":
                    print "Error :value for the '"+arg+"' must be a integer."
                if error_type == "not_alpha":
                    print "Error :value for the '"+arg+"' must be alphabets only."
                if error_type == "empty":
                    print "Error : No arguments in the input"
                if error_type == "req_missing":
                    print "Error : required argument --"+arg+" is missing from input."

    def check_value(self, check_for, key, value):
        """check for values integrity """
        if check_for == "Integer":
            if value.isdigit():
                self.key_store(key, value)
            else:
                self.error_store("not_int", key)
        elif check_for == "String":
            if value.isalpha():
                self.key_store(key, value)
            else:
                self.error_store("not_alpha", key)
        elif check_for == "Alpha_num":
            self.key_store(key, value)
        elif check_for == "user_defined":
            self.key_store(key, value)

    def result_display(self):
        """function to print result as JSON"""
        print '{'
        for key in json:
            for val in json[key]:
                print "'"+key+"'"+"='"+val+"'"
        print '}'

    def display(self, set_name):
        """function to display values in set"""
        for args in set_name:
            print '\n'+args +" :"
            for cur_arg in arg_detail[args]:
                key = cur_arg.partition("=")[0]                    #separating key and value
                value = cur_arg.partition("=")[2]
                print key +" : "+ value

    def help(self):
        """function to display argument details"""
        print "\n optional arguments :"
        self.display(optional)
        print "\n required arguments :"
        self.display(required)

    def check_required(self):
        """function to check for required arguments in input"""
        for args in required:
            if args not in Input:
                self.error_store("req_missing", args)


def main():
    """function to execute Parser class"""

    obj = Parser()

    obj.add_argument("--key", Type="integer", Help="stores name")
    obj.add_argument("-name", Type="string", Mandatory="True")
    obj.add_argument("--roll", Type="alpha_num")

    num_of_args = len(sys.argv)    

    if num_of_args == 1:                                           #check if arguments are provided
        obj.error_store("empty", "empty")
        obj.error_display()
        return 0

    for cur_arg in range(1, num_of_args):                        #iterating over all arguments
        arg = sys.argv[cur_arg]

        if arg == "-h" or arg == "-help":         
            obj.help()
            continue
            
        key = arg.partition("=")[0]            
        value = arg.partition("=")[2]
        Input.add(key)                           

        if "=" not in arg:                                       #checking for value
            obj.error_store("no_input", key)
            continue

        if key in Integer:
            obj.check_value("Integer", key, value)                 #check for recognized argument
        elif key in String:
            obj.check_value("String", key, value)
        elif key in Alpha_num:
            obj.check_value("Alpha_num", key, value)
        elif key in ambig:
            obj.check_value("user_defined", key, value)
        else:
            obj.error_store("not_support", key)

    obj.check_required()

    if bool(error):                                           #check if error dictionary is empty
        obj.error_display()
    else:                                                       #displaying output if no error found
        obj.result_display()


if __name__ == "__main__":
    main()
