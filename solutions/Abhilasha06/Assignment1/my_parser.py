# -*- coding: utf-8 -*-

"""
Created on Sun Aug 25 15:21:34 2019
@author: Abhilasha
"""
class Error(Exception):

    """
    Error class
    """

    def __init__(self, message):
        super(Error, self).__init__(message)
        
        
class Option(object):

    """
    filed_name - name of the fields
    dtype - type that tese fields store
    nargs - number of arguments given for the fields
    """

    def __init__(self,  field_name, dtype, nargs):
        self.field_name = field_name
        self.dtype = dtype
        self.nargs = nargs

       
class MyParser:
    """
    command line parser
    """
    def __init__(self):
        self.options=[]
        self.data={}
        

    def add_option(self, field_name, dtype, nargs):
        option_being_added = Option(field_name, dtype, nargs)
        self.options.append(option_being_added)
        
    
    def check_key(self, field_type, given_type, field_size, given_size):
        """
        to check if the key is valid or not
        """
        
        import re
        if field_size != given_size:
            raise Error("invalid number of arguments for --key")
            
        elif bool(re.match('^[0-9]+$', given_type)):
            self.data["--key"] = given_type
            
        elif bool(re.match('^[0-9]+$', given_type)) == False:
            raise Error("The --key argument has invalid value.")
            
            
    def check_name(self, field_type, given_type, field_size, given_size):
        """
        to check if the key is valid or not
        """
        
        if field_size != given_size:
            raise Error("invalid number of arguments for --name")
            
        elif given_type.isalpha() == False:
            raise Error("The --name argument has invalid value.")
            
        else:
            self.data["--name"] = given_type
      
    
    def check_local(self, field_type, given_type, field_size, given_size):
        """
        to check if local is valid or not
        """
        
        if field_size != given_size:
            raise Error("Invalid number of arguments for --local")
            
        elif given_type.isalpha() == False:
            raise Error("The --local argument has invalid value.")
            
        else:
            self.data["local"] = given_type
        
    
    def check_remote(self, field_type, given_type, field_size, given_size):
        """
        to check if remote is valid or not
        """
        if field_size != given_size:
            raise Error("Invalid number of arguments for --remote")
            
        elif given_type.isalpha() == False:
            raise Error("The --remote argument has invalid value.")
            
        else:
            self.data["remote"] = given_type
            
            
    def check_argument(self, argument):
        """
        to parse the given input and give error if it is invalid
        """
        import json
        argument = list(argument.split(" "))
        no_of_args = len(argument)

        
        if no_of_args == 1:
            raise Error("No arguments.")
            
        for args in argument[1:]:
            splitted_word = args.split('=')
            size = len(splitted_word)
            flag=0
            
            for opt in self.options:
            
                if (splitted_word[0] == opt.field_name) :
                    flag=1
                    if(splitted_word[0] == "--key"):
                        self.check_key(opt.field_name, splitted_word[1], opt.nargs, size)
                        
                    elif(splitted_word[0] == "--name"):
                        self.check_name(opt.field_name, splitted_word[1], opt.nargs, size)
                        
                    elif(splitted_word[0] == "--local"):
                        if opt.nargs == size and size == 2:
                            self.check_key(opt.field_name, splitted_word[1], opt.nargs, size)
                        elif opt.nargs == size and size == 1:
                            self.data["--local"] = "true"
                            
                    elif(splitted_word[0]=="--remote"):
                        if opt.nargs == size and size == 2:
                            self.check_key(opt.dtype, splitted_word[1], opt.nargs, size)
                        elif size == 1:
                            self.data["--remote"] = "true"
                            
            if flag==0:
                raise Error("Invalid field given.")
          
        return(json.dumps(self.data))
     