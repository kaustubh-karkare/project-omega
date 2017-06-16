import sys

def main():
    
    num_of_args = len(sys.argv)                         # store number of arguments
    
    if num_of_args == 1 :
        print("No arguments in the input")
    
    else :
        key,value,flag=0
        for cur_arg in range(1,num_of_args) :           # traverse through all arguments
            
            arg = sys.argv[i]
            if arg[0:6]== "--key=" :
                
                if len(arg) == 6 :                # check if not empty
                     flag=1
                     break
                    
                elif arg[6: ].isdigit():           #check if key is digit
                    key.append(arg[6: ])
                    
                else :                              
                    flag=2
                    break
                 
            elif arg[0:8]== "--value=" :

                if len(arg) == 8 :
                    flag=1
                    break
                
                else :
                    value.append(arg[8:])

            else :
                
                flag=3
                break

        if flag==0 :
            
            print('{')                                          #print as JSON
            for i in range(0,len(key)) :
                print('"key": "' + key[0] + '",')
                
            for i in range(0,len(value)) :
                print('"name": "' + key[0] + '",')
                
            print('}')
        
        elif flag==1 :
            print("Error: The argument is required, but missing from input.")                      #print Errors

        elif flag==2 :
            print("Error: The value for the '--key' argument must be a positive integer.")

        else :
            print("Error : Arguments type not suported")


if __name__=="__main__" : main()
        
            
        
                       

                
                
        
            
            

    

