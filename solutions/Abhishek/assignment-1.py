import sys
import json

String,Integer,required,optional,Alpha_num,input  = set(),set(),set(),set(),set(),set()         #set objects
error,json,arg_detail= dict(),dict(),dict()                                                     #dictionary objects


class parser :
    """ class to deal with argumetn parsing"""

    def add_argument(self, *args):
        """method to add new argument to framework"""
        key = args[0].partition("=")[0]                              #separating key and value part of an argument
        arg_name =  args[0].partition("=")[2]
        
        for i in range(1,len(args)) :                               #iterating over different parameters passed in add_argment()
            key = args[i].partition("=")[0]                              
            value =  args[i].partition("=")[2]
            required_chk=0                                              # for checking of mandatory argument 
            
            if key=="Type" :
                if value=="integer" :                                   #storing key in set according to respective type
                    Integer.add(arg_name)
                elif value=="string" :
                    String.add(arg_name)
                elif value=="alpha_num" :
                    Alpha_num.add(arg_name)
            if key=="mandatoy" :
                required.add(arg_name)
                required_chk=1
            
            arg_detail.setdefault(arg_name,[]).append(args[i])

        if required_chk==0:
              optional.add(arg_name)

    def error_store(self,error_type,key):
        """function to store errors"""
        if error_type==0:
            error.setdefault("error_0",[]).append(key)                  #inserting errors in error dictionary
        if error_type == 2 :
            error.setdefault("error_0=2",[]).append(key)
        if error_type == 3 :
            error.setdefault("error_3",[]).append(key)
        if error_type == 1 :
            error.setdefault("error_1",[]).append(key)
        if error_type == 4 :
            error.setdefault("error_4",[]).append(key)
        if error_type == 5 :
            error.setdefault("error_5",[]).append(key)

    def key_store(self,key,value) :
        """function to add new value to an argument"""
        json.setdefault(key[2:],[]).append(value)               
        
    def error_display(self):
        """function to display the errors to user"""
        for error_type in error.keys() :                                      
            if error_type=="error_0" :                    
                for arg in error[error_type] :
                    print("Error : The value for '"+arg+"'argument is empty.")
            if error_type=="error_1" :
                for arg in error[error_type] :
                    print("Error : The argument '"+arg+"' is not supported by program.")
            if error_type=="error_2" :
                for arg in error[error_type] :
                    print("Error : The value for the '"+arg+"' argument must be a positive integer.")
            if error_type=="error_3" :
                for arg in error[error_type] :
                    print("Error : The value for the '"+arg+"' argument must consist of alphabets only.")
            if error_type=="error_4" :
                  print("Error : No arguments in the input")
            if error_type=="error_5" :                    
                for arg in error[error_type] :
                    print("Error : The required argumen --"+arg+" is missing from input.")
            

    def result_display(self):
        """function to print result as JSON"""
        print('{')                                          
        for key in json.keys() :
            for val in json[key]:
                print("'"+key+"'"+"='"+val+"'")
        print('}')

    def help(self):
        """function to display argument details"""
        print("\n optional arguments :")
        for args in optional:
            print('\n'+args +" :")
            for h in arg_detail[args]:
                key = h.partition("=")[0]                              #separating key and value part of an argument
                value =  h.partition("=")[2]
                print(key +" : "+ value)

        print("\n required arguments :")
        for args in required:
            print('\n'+args +": ")
            for h in arg_detail[args]:
                key = h.partition("=")[0]                              
                value =  h.partition("=")[2]
                print(key +" : "+ value)


    def check_required(self):
        """function to check for required arguments in input"""
        for args in required :
            found=0
            for arg_input in input :
                if arg_input==args:
                    found=1

            if found==0 :
                error_store(5,args)
                
            

def main():
    
    
    obj = parser()                                          #creating new object of class parser
    
    """obj.add_argument("Name=argument_name","Type=data_type","Help="this is help message","Mandatory=True")"""   # adding arguments to be recognized by main program
    obj.add_argument("Name=--key","Type=integer",
                        "Help=it stores name")                                    
    obj.add_argument("Name=--name","Type=string")
    obj.add_argument("Name=--roll","Type=alpha_num")

    num_of_args = len(sys.argv)                                    

    if num_of_args == 1 :                                            #check if arguments are provided
        obj.error_store(4,"empty")                    
    else :

        for cur_arg in range(1,num_of_args) :                        #iterating over all arguments
            arg = sys.argv[cur_arg]
            
            if arg=="-h" or arg=="-help" :                          
                obj.help()
                continue
            
            key = arg.partition("=")[0]                             #separating key and value part of an argument
            value =  arg.partition("=")[2]
            input.add(key)                                         

            if "=" not in arg :                                       #checking whether the value is provided for argument
                obj.error_store(0,key)
            else : 
                if key in Integer :                                    #checking whether the argument are recognized or not/arguments present in set or not
                    if value.isdigit()==True :
                        obj.key_store(key,value)
                    else :
                        obj.error_store(2,key)
                elif key in String :
                    if value.isalpha()==True :
                        obj.key_store(key,value)
                    else :                                                    
                        obj.error_store(3,key)                          #inserting errors
                elif key in Alpha_num :
                        obj.key_store(key,value)
                else :
                    obj.error_store(1,key)

                    

    obj.check_required()                    

    if bool(error) :                                                     #to check if error dictionary is empty
        obj.error_display()
    else :                                                              #displaying output if no error found
        obj.result_display()


if __name__=="__main__" : main()
