# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 15:21:34 2019

@author: Abhilasha
"""



class cli:
  
             

    def check_argument(self,argument):
        
        import re
        import json
        
        #to store the data as a json file
        data={}

        #list of valid fields
        list_of_fields=["--key","--local","--remote","--name"]
        argument = list(argument.split(" "))


        no_of_args=(int)(format(len(argument)))
        if (no_of_args == 1):

            return("Error: The '--key' argument is required, but missing from input.")
        
        if (no_of_args>5):

            return("Error: Too many arguments")

        
        for args in argument[1:]:
            
            splitted_word=args.split('=')
            l=int(len(splitted_word))
            if(l>2):
                return("Error: Invalid argument")
            
            elif(splitted_word[0] not in list_of_fields):
                return("Error: Field not defined")
    
            elif(splitted_word[0]=="--key"):
                if("--key" in data):
                    return("Error: --key can't occur more than once")
                
                elif(l!=2):
                    return("Error: --key can't be empty")
                   
                
                if(bool(re.match('^[0-9]+$', splitted_word[1])) ):
                    data["--key"]=splitted_word[1]
                
                else:
                    return("Error: The value for the '--key' argument must be a positive integer.")
                   

        
            elif(splitted_word[0]=="--name"):
                if(l!=2):
                    return("Error: --name can't be empty")
                
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
                    return("Erroe: --remote takes no value")
                    return 0
                elif("--local" in data):
                    return("Error: --local and --remote can't occur together")
                   
                else:
                    data["--remote"]="true"
                    
        if("--key" not in data):
            return("Error: The '--key' argument is required, but missing from input.")
            
        else: 
            return(json.dumps(data))
            
            
            
            












        

        

        


    

