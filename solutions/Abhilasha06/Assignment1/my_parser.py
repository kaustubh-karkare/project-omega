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

    def __init__(self, name, dtype, is_flag):
        self.name = name
        self.dtype = dtype
        self.is_flag = is_flag

       
class MyParser:
    """
    command line parser
    """
    def __init__(self):
        self.options = []


    def add_option(self, name, dtype, is_flag):
        option_being_added = Option(name, dtype, is_flag)
        self.options.append(option_being_added)
        
    
    def check_dtype(self, field_name, given_type, given_value, data):
        """
        to check if the datatype of the given arguments are valid
        """
        if given_type == "str":
            
            data[field_name] = given_value  
         
            
        elif given_type == "int":
            
            if given_value.isdigit():
                data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
                
        elif given_type == "bool":
            
            if given_value == "True" or given_value == "False":
                data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
            
        
    def check_options(self, arguments):
        """
        to parse the given input and give error if it is invalid
        """
        no_of_args = len(arguments)
        data = {}
        
        if no_of_args == 1:
            raise MyParserError("No options given.")
            
        for args in arguments[1:]:
            splitted_word = args.split('=')
            size = len(splitted_word)
            found_option = False
            
            for opt in self.options:
                if splitted_word[0] == opt.name:
              
                    found_option = True

                    if size > 2:
                        raise MyParserError("Too many arguments.")
                        
                    elif size == 1:
                        if not opt.is_flag:
                            data[opt.name] = "True"
                        elif opt.is_flag:
                            raise MyParserError("Too less arguments.")
                            
                         
                    elif size == 2:
                        if not opt.is_flag:
                            raise MyParserError("Too many arguments.")
                        elif opt.is_flag:
                            self.check_dtype(splitted_word[0], opt.dtype, splitted_word[1], data)
                
                            
            if not found_option:
                raise MyParserError("Unexpected field given.")
          
        return data
     