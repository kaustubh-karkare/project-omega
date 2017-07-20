import sys
import json

String = set()                                                    #different sets to store arguments of specific type
Integer = set()
Alpha_num = set()
error=dict()                                                #dictionary object to store error details

class parser :
    
    def add_argument(self, Name , Type):                            # method to add new argument to framework 

        if Type=="Integer" :
            Integer.add(Name)

        elif Type=="String" :
            String.add(Name)

        elif Type=="Alpha_num" :
            Alpha_num.add(Name)


def main():
    
    error.clear()
    
    obj = parser()                                          #crating new object of class parser

    #obj.add_argument("argument_name","data_type")           # adding arguments to be recognized by main program
    #obj.add_argument("--key","Integer")                                    
    #obj.add_argument("--name","String")

    num_of_args = len(sys.argv)                         # store number of arguments

    if num_of_args == 1 :                               #check if arguments are provided
        error["error_4"] = ["empty"]                    

    else :
        
        json = dict()
        json.clear()

        for cur_arg in range(1,num_of_args) :                        #iterating over all arguments

            arg = sys.argv[cur_arg]
            
            key = arg.partition("=")[0]                              #separating key and value part of an argument
            value =  arg.partition("=")[2]

            if "=" not in arg :                                     #checking whether the value is provided for argument

                error_type=0
                if "error_0" in error :                             #inserting errors in error dictionary
                    error["error_0"].append(key)
                else :
                    error["error_0"] = [key]
                

            else : 

                if key in Integer :                                 #checking whether the argument are recognized or not/arguments present in set or not


                    if value.isdigit()==True :
                    
                        if key[2:] in json :
                             json[key[2:]].append(value)                     # adding new value to an existing argument
                        else :
                             json[key[2:]] = [value]                  #adding new argument to dictionary
                    
                    else :
                        error_type = 2
                        if "error_2" in error :
                            error["error_2"].append(key)
                        else :
                            error["error_2"] = [key]
                

                

                elif key in String :

                    if value.isalpha()==True :

                        if key[2:] in json :
                             json[key[2:]].append(value)                     # add new value to an existing argument
                        else :
                             json[key[2:]] = [value]

                    else :                                                    #inserting errors
                        error_type = 2
                        if "error_3" in error :
                            error["error_3"].append(key)
                        else :
                            error["error_3"] = [key]
                        
                    
                    
                elif key in Alpha_num :

                    if key[2:] in json :
                             json[key[2:]].append(value)                     # add new value to an existing argument
                    else :
                         json[key[2:]] = [value]

                


                else :
                    error_type = 1
                    if "error_1" in error :
                        error["error_1"].append(key)
                    else :
                        error["error_1"] = [key]

    


    if bool(error) :                                                              #to check if error dictionary is empty

          for error_type in error.keys() :                                      #displaying all the errors to user

              if error_type=="error_0" :                    

                  for arg in error[error_type] :
                      print("Error : The value for '"+arg+"' argument is empty.")
                    

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


              
                      

    else :                                                  #displaying output if no error found

        print('{')                                          #print as JSON
        for key in json.keys() :
            for val in json[key]:
                print("'"+key+"'"+"='"+val+"'")
        print('}')


    





if __name__=="__main__" : main()
