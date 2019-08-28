argparser
---------

Three class ArgumentParser, Option, ParsingError

Option
------
This class represents a type of option which has the following features
name : The name of the option (For this assignment only optional arguments are implemented which has a prefix '--')

action : It is a function which takes a list of arguments as a parameter and generates the desired output. We can create our custom action function and pass the function with the action parameter. By default the action is 'store' i.e simply storing the arguments. (Refer to test.py for examples)

nargs : It defines the number of arguments required for the option. By default it can take any number of arguments. Supported types are ( Any integer(N), '+' -> 1 or more than 1 arguments, '?' -> 0 or 1 argument, '*' -> any number of arguments)

repeat : It is of boolean type which if True signifes that an option can occur multiple times in the input. By default repeat is set to False.

Note: Each option should come before its arguments
i.e "--sum 1 2 4" is correct
    "1 2 4 --sum" is incorrect


ArgumentParser
--------------
This class allows to create command line options.
A command line option can be created with the help of add_argument() method

add_argument(name, action=None, nargs=None, type=None, repeat=None) : is used to create a Option object

add_mutually_exclusive_group() : sets the group to be mutually exclusive i.e only 1 of the given optional arguments are allowed.

arg_parse(args : List) : It takes a list of arguments(sys.argv) and generates the correct output in the form of json or returns a ParsingError if some error is occured.


ParsingError
------------
This class implements the custom error to be used for validating errors related to parsing only.
