# -*- coding: utf-8 -*-

"""
Created on Sun Aug 25 15:21:34 2019
@author: Abhilasha
"""
class MyParserError(Exception):

    """
    Error class
    """

    def __init__(self, message):
        super(MyParserError, self).__init__(message)
        
        
class Option(object):

    """
    options
    """

    def __init__(self, name, dtype, is_required):
        self.name = name
        self.dtype = dtype
        self.is_required = is_required

       
class MyParser:
    """
    command line parser
    """
    def __init__(self):
        self.options = []
        self.data = {}
        

    def add_option(self, name, dtype, is_required):
        option_being_added = Option(name, dtype, is_required)
        self.options.append(option_being_added)
        
    
    def check_dtype(self, field_name, given_type, given_value):
        """
        to check if the datatype of the given arguments are valid
        """
        if given_type == "str":
            
            self.data[field_name] = given_value  
         
            
        elif given_type == "int":
            
            if given_value.isdigit():
                self.data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
                
        elif given_type == "bool":
            
            if given_value == "True" or given_value == "False":
                self.data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
            
        
    def check_options(self, argument):
        """
        to parse the given input and give error if it is invalid
        """
        no_of_args = len(argument)
        
        if no_of_args == 1:
            raise MyParserError("No options given.")
            
        for args in argument[1:]:
            splitted_word = args.split('=')
            size = len(splitted_word)
            flag = 0
            
            for opt in self.options:
                if splitted_word[0] == opt.name:
              
                    flag = 1

                    if size > 2:
                        raise MyParserError("Too many arguments.")
                        
                    elif size == 1 and opt.is_required == "False":
                        self.data[opt.name] = "True"
                         
                    else:
                        if opt.is_required == "False" and size == 2:
                            raise MyParserError("Too many arguments.")
                        elif opt.is_required == "True" and size == 1:
                            raise MyParserError("Too less arguments.")
                        else:
                            self.check_dtype(splitted_word[0], opt.dtype, splitted_word[1])
                
                            
            if flag == 0:
                raise MyParserError("Invalid field given.")
          
        return self.data
     