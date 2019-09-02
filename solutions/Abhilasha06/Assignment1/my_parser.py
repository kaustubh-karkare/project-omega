# -*- coding: utf-8 -*-

"""
Created on Sun Aug 25 15:21:34 2019
@author: Abhilasha
"""
import re

class MyParserError(Exception):

    """
    Error class
    """

    def __init__(self, message):
        super(MyParserError, self).__init__(message)
        
        
class Option(object):

    """
    filed_name - name of the fields
    dtype - type that tese fields store
    nargs - number of arguments given for the fields
    """

    def __init__(self,  name, dtype, nargs):
        self.name = name
        self.dtype = dtype
        self.nargs = nargs

       
class MyParser:
    """
    command line parser
    """
    def __init__(self):
        self.options=[]
        self.data={}
        

    def add_option(self, name, dtype, nargs):
        option_being_added = Option(name, dtype, nargs)
        self.options.append(option_being_added)
        
        
    def check_size(self, field_size, given_size):
        """
        to check if the no of arguments given is valid
        """      
        if field_size != given_size:
            raise MyParserError("Invalid number of arguments.")
        
    
    def check_dtype(self,field_name, given_type, given_value, size):
        """
        to check if the datatype of the given arguments are valid
        """
        if given_type == "str":
            
            if given_value.isalpha():
                self.data[field_name] = given_value  
            else:
                raise MyParserError("The field has invalid value.")
            
        elif given_type == "int":
            
            if bool(re.match('^[0-9]+$',given_value)):
                self.data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
                
        elif given_type == "bool":
            
            if given_value == "True" or given_value == "False":
                 self.data[field_name] = given_value
            else:
                raise MyParserError("The field has invalid value.")
            
        
    def check_argument(self, argument):
        """
        to parse the given input and give error if it is invalid
        """
        no_of_args = len(argument)
        
        if no_of_args == 1:
            raise MyParserError("No arguments.")
            
        for args in argument[1:]:
            splitted_word = args.split('=')
            size = len(splitted_word)
            flag = 0
            
            for opt in self.options:
                if (splitted_word[0] == opt.name):
              
                    flag = 1
                
                    self.check_size(opt.nargs, size)
                    if size == 1:
                         self.data[opt.name] = "True"
                    else:
                        self.check_dtype(splitted_word[0], opt.dtype, splitted_word[1],size)
                
                            
            if flag == 0:
                raise MyParserError("Invalid field given.")
          
        return(self.data)
     