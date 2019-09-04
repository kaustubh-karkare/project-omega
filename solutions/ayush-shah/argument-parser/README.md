# Examples
```
$ python3 parser.py --key=1234 --name=ayush                             
   { "--key": "1234, "--name": "ayush" }                                                                    
                                                                        
$ python3 parser.py --key=ayush                                         
  Error: The value for argument '--key' must be integer                 
                                                                        
$ python3 parser.py --name=ayush                                        
  Error: The argument '--key' is required, but missing from input       
                                                                        
$ python3 parser.py                                                     
  Error: The argument '--key' is required, but missing from input       
                                                                        
$ python3 parser.py --local --remote                                    
  Error: The '--local' and '--remote' arguments cannot be used together 
  Error: The argument '--key' is required, but missing from input       
                                                                        
$ python3 parser.py --key=1234 --roll=10014                             
  Error: invalid argument '--roll'                                      
                                                                        
$ python3 parser.py --key                                               
  Error: The value for argument '--key' is missing                      
```
