import sys

def main():
    
    num_of_args = len(sys.argv)                         # store number of arguments
    
    if num_of_args == 1 :
        print("No arguments in the input")
    
    else :
        flag=0
        json = dict()                                    #dictionary to store arguments and values
        for cur_arg in range(1,num_of_args) :           # traverse through all arguments
            
            arg = sys.argv[cur_arg]
            if len(arg)>=5:                            #check for length of argument
                

                if arg[0]=='-' and arg[1]=='-' :
                     
                     i=2
                     intr_flag = 0
                     while i<len(arg):                #check if a valid argument
                         if arg[i]=='=' :
                             intr_flag = 1
                             break
                         i=i+1;
                            
                     if intr_flag == 0 or i == len(arg) :
                         flag = 1
                         break

                     if arg[2:i] in json :
                         json[arg[2:i]].append(arg[i+1:])                     # add new value to an existing argument
                     else :
                         json[arg[2:i]] = [arg[i+1:]]                  #add new argument to dictionary


                else :
                         flag=3
                         break


            else :
                    flag=3
                    break

                
              
                            
                    
           

        if flag==0 :
            
            print('{')                                          #print as JSON
            for key in json.keys() :
                for val in json[key]:
                    print("'"+key+"'"+"'='"+val+"'")    
            print('}')
        
        elif flag==1 :
            print("Error: The argument is required, but missing from input.")                      #print Errors

        elif flag==2 :
            print("Error: The value for the '--key' argument must be a positive integer.")

        elif flag==3 :
            print("Error : Arguments type not suported")


if __name__=="__main__" : main()
      
