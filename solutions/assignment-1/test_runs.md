# Test runs:

drs_11@Asbestos:~/Documents/programming/Omega/ass1$ python test.py --key=123 --name=DR                                                                                  
{"key": 123, "name": "DR"}  

drs_11@Asbestos:~/Documents/programming/Omega/ass1$ python test.py --key=cat
Traceback (most recent call last):
  File "test.py", line 9, in <module>                                               
    parser.parse_arguments()                                                        
  File "/home/drs_11/Documents/programming/Omega/ass1/CLIparser.py", line 54, in parse_arguments                                                                               
    raise WrongTypeError(type(value), self.args[arg].arg_type, arg)                 
v2.WrongTypeError: str type argument added instead of int for key

drs_11@Asbestos:~/Documents/programming/Omega/ass1$ python test.py
Traceback (most recent call last):                                                  
  File "test.py", line 9, in <module>                                               
    parser.parse_arguments()                                                        
  File "/home/drs_11/Documents/programming/Omega/ass1/CLIparser.py", line 71, in parse_arguments                                                                               
    raise ReqArgError(argument)                                                     
v2.ReqArgError: Error: The 'key'  argument is required but missing from the input.  


drs_11@Asbestos:~/Documents/programming/Omega/ass1$ python test.py --remote --local
Traceback (most recent call last):                                                  
  File "test.py", line 9, in <module>                                               
    parser.parse_arguments()
  File "/home/drs_11/Documents/programming/Omega/ass1/CLIparser.py", line 66, in parse_arguments
    raise SimultaneousUsageError(arg, self.args[arg].cant_be_used_with)
v2.SimultaneousUsageError: local cannot be used with these arguments: ['remote']
