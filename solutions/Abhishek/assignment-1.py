import sys
import json

String, Integer, required, optional = set(), set(), set(), set()
Alpha_num, input, ambig  = set(), set(), set()       
error, json, arg_detail= dict(),dict(),dict()                                           

class Parser :
    """ class to deal with argument parsing"""

    def add_argument(self,name, **kwargs):
        """method to add new argument to framework"""
        for key in kwargs:                               #iterating over different parameters passed in add_argment()
            value = kwargs[key]                                             # for checking of mandatory argument 
            
            if key == "Type":
                if value == "integer":                                   #storing key in set according to respective type
                    Integer.add(name)
                elif value == "string":
                    String.add(name)
                elif value == "alpha_num":
                    Alpha_num.add(name)
                else:
                    ambig.add(name)
            if key == "mandatory" and value=="True":
                required.add(value)
            else:
                optional.add(value)
            
            arg_detail.setdefault(name, []).append(value)

    def error_store(self, error_type, key):
        """function to store errors"""                                          #storing type of error
        error.setdefault(error_type, []).append(key) 

    def key_store(self, key, value):
        """function to add new value to an argument"""
        json.setdefault(key[2:], []).append(value)               
        
    def error_display(self):
        """function to display the errors to user"""
        for error_type in error.keys():
            for arg in error[error_type]:                                     
                if error_type == "no_input":                    
                    print("Error :value for '"+arg+"'argument is empty.")
                if error_type == "not_support":
                        print("Error :argument '"+arg+"'is not supported.")
                if error_type == "not_int":
                        print("Error :value for the '"+arg+"' must be a integer.")
                if error_type == "not_alpha":
                        print("Error :value for the '"+arg+"' must be alphabets only.")
                if error_type == "empty":
                      print("Error : No arguments in the input")
                if error_type == "req_missing":
                        print("Error : required argument --"+arg+" is missing from input.")
            

    def result_display(self):
        """function to print result as JSON"""
        print('{')                                          
        for key in json.keys():
            for val in json[key]:
                print("'"+key+"'"+"='"+val+"'")
        print('}')

    def help(self):
        """function to display argument details"""
        print("\n optional arguments :")
        display(optional)
        print("\n required arguments :")
        display(required)

    def display(set):
        """function to display values in set"""
        for args in set:
            print('\n'+args +" :")
            for h in arg_detail[args]:
                key = h.partition("=")[0]                              #separating key and value part of argument
                value =  h.partition("=")[2]
                print(key +" : "+ value)


    def check_required(self):
        """function to check for required arguments in input"""
        for args in required:
            if args not in input:
                error_store("req_missing", args)
                
            
def main():
    
    obj = Parser()                                         
    
    """obj.add_argument("argument_name", Type="data_type",
                             Help="help message", Mandatory="True")"""    # adding arguments to be recognized by program
    obj.add_argument("--key", Type="integer",
                            Help="it stores name")                                    
    obj.add_argument("-name", Type="string")
    obj.add_argument("--roll", Type="alpha_num")

    num_of_args = len(sys.argv)                                    

    if num_of_args == 1:                                            #check if arguments are provided
        obj.error_store("empty", "empty")                    
    else :

        for cur_arg in range(1, num_of_args):                        #iterating over all arguments
            arg = sys.argv[cur_arg]
            
            if arg == "-h" or arg == "-help":                          
                obj.help()
                continue
            
            key = arg.partition("=")[0]                            
            value = arg.partition("=")[2]
            input.add(key)                                         

            if "=" not in arg:                                       #checking whether the value is provided for argument
                obj.error_store("no_input", key)
            else: 
                if key in Integer:                                    #checking whether the argument are recognized
                    if value.isdigit() == True:
                        obj.key_store(key, value)
                    else:
                        obj.error_store("not_int", key)
                elif key in String:
                    if value.isalpha() == True:
                        obj.key_store(key, value)
                    else:                                                    
                        obj.error_store("not_alpha", key)                          #inserting errors
                elif key in Alpha_num:
                    obj.key_store(key, value)
                elif ley in ambig:
                    obj.key_store(key, value)
                else:
                    obj.error_store("not_support", key)

                    
    obj.check_required()                    

    if bool(error):                                                     #to check if error dictionary is empty
        obj.error_display()
    else :                                                              #displaying output if no error found
        obj.result_display()


if __name__=="__main__" : main()
