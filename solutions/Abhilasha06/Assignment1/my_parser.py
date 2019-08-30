# -*- coding: utf-8 -*-

"""
Created on Sun Aug 25 15:21:34 2019
@author: Abhilasha
"""
class MyParser:
    """
    command line parser
    """
    @classmethod
    def add_option(cls, option_name, option_type, reqirement):
        """
        adding the options
        """
        list_of_fields = []
        list_of_fields.append(option_name)
    @classmethod
    def check_key(cls, size, value, data):
        """
        to check if the key is valid or not
        """
        import re
        if "--key" in data:
            mssg = "Error: --key can't occur more than once"
        elif size != 2:
            mssg = "Error: --key can't be empty"
        elif bool(re.match('^[0-9]+$', value)):
            data["--key"] = value
            mssg = "successful"
        else:
            mssg = "Error: The value for the '--key' argument must be a positive integer."
        return mssg
    @classmethod
    def check_local(cls, size, data):
        """
        to check if local is valid or not
        """
        if size != 1:
            mssg1 = "Error: --local takes no value"
        elif "--remote" in data:
            mssg1 = "Error: --local and --remote can't occur together"
        else:
            data["--local"] = "true"
            mssg1 = "successful"
        return mssg1
    @classmethod
    def check_remote(cls, size, data):
        """
        to check if remote is valid or not
        """
        if size != 1:
            mssg2 = "Error: --remote takes no value"
        elif "--local" in data:
            mssg2 = "Error: --local and --remote can't occur together"
        else:
            data["--remote"] = "true"
            mssg2 = "successful"
        return mssg2
    @classmethod
    def check_argument(cls, argument):
        """
        to parse the given input and give error if it is invalid
        """
        import json
        data = {}
        list_of_fields = ["--key", "--local", "--remote", "--name"]
        argument = list(argument.split(" "))
        no_of_args = (int)(format(len(argument)))
        if no_of_args == 1:
            ans = "Error: The '--key' argument is required, but missing from input."
        for args in argument[1:]:
            splitted_word = args.split('=')
            size = int(len(splitted_word))
            if size > 2:
                ans = "Error: Invalid argument"
            elif splitted_word[0] not in list_of_fields:
                return"Error: Field not defined"
            elif splitted_word[0] == "--key":
                ans = cls.check_key(size, splitted_word[1], data)
            elif splitted_word[0] == "--name":
                if size != 2:
                    ans = "Error: --name can't be empty"
                else:
                    data["--name"] = splitted_word[1]
            elif splitted_word[0] == "--local":
                ans = cls.check_local(size, data)
            else:
                ans = cls.check_remote(size, data)
        if "--key" not in data:
            ans = "Error: The '--key' argument is required, but missing or has invalid value."
        elif ans == "successful":
            ans = json.dumps(data)
        return ans
