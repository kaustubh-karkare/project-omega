# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 15:21:34 2019

@author: Abhilasha
"""

import sys
import re
import json

#to store the data as a json file
data={}

#list of valid fields
list_of_fields=["--key","--local","--remote","--name"]


no_of_args=(int)(format(len(sys.argv)))

class cli:
             

    def check_argument(self,argument):
        
        
        for args in argument[1:]:
            
            splitted_word=args.split('=')
            l=int(len(splitted_word))
            if(l>2):
                print("Error: Invalid argument")
                return 0
            
            elif(splitted_word[0] not in list_of_fields):
                print("Error: Field "+splitted_word[0]+" not defined")
                return 0
    
            elif(splitted_word[0]=="--key"):
                if("--key" in data):
                    print("Error: --key can't occur more than once")
                    return 0
                elif(l!=2):
                    print("Error: --key can't be empty")
                    return 0
                
                if(bool(re.match('^[0-9]+$', splitted_word[1])) ):
                    data["--key"]=splitted_word[1]
                
                else:
                    print("Error: The value for the '--key' argument must be a positive integer.")
                    return 0

        
            elif(splitted_word[0]=="--name"):
                if(l!=2):
                    print("Error: --name can't be empty")
                    return 0
                else:
                    data["--name"]=splitted_word[1]
                    
            
        
            elif(splitted_word[0]=="--local"):
                if(l!=1):
                    print("Error: --local takes no value")
                    return 0
                elif("--remote" in data):
                    print("Error: --local and --remote can't occur together")
                    return 0
                else:
                    data["--local"]="true"
                 
        
            elif(splitted_word[0]=="--remote"):
                if(l!=1):
                    print("Erroe: --remote takes no value")
                    return 0
                elif("--local" in data):
                    print("Error: --local and --remote can't occur together")
                    return 0
                else:
                    data["--remote"]="true"
                    
        if("--key" not in data):
            print("Error: The '--key' argument is required, but missing from input.")
            return 0
        else: 
            return(json.dumps(data))
                


cli_obj=cli()


#minimum 1 field and maximum four fields are allowed
if (no_of_args == 1):

    print("Error: The '--key' argument is required, but missing from input.")


elif(no_of_args>5):
    print("Error: Too many arguments")
    
else:

   
    p=cli_obj.check_argument(sys.argv)


    if(p!=0):
        print(p)
        

        


    

