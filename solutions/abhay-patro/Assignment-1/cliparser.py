# MODULE ->CLIPARSER
# Author-> Abhay Charan Patro ,CSE 2K18 , BIT MESRA

# imported the json module to output in JSON
import json

# A list to store the arguments given through command line so as to check if all required arguments are given or not
givenarg=[]
# A list to add arguments with the help of add_option function
options=[]
# A list to store the inputed argument and its value
inputs=[]
# A list to store the pair of arguments which cannot be used together
cannot_be_used_with = []

# A function to add arguments
def add_option(name_of_argument,type,required,*args):
        options.append((name_of_argument,type,required))
        for arg in args:
             if (arg,name_of_argument) not in cannot_be_used_with:
                 cannot_be_used_with.append((name_of_argument,arg))
# A function to parse teh given command line argument


def parse(command):
    # A variable noerror to check if errors are present or not
    noerror=1

    # Extracts the argument and its value from the command line and stores in inputs
    for i in range(len(command)):
        for  option , t , req in options:
            if option in command[i]:
                for k in range(len(command[i])):
                    if command[i][k]=="=":
                        value=command[i][k+1:]
                        givenarg.append(option)
                        inputs.append((option, value))
            
    # Checks if two arguments which cannot be used together are there or not
    for arg1 ,arg2 in cannot_be_used_with :
        if arg1  in givenarg and arg2  in givenarg:
            noerror=0
            print(arg1," and ",arg2," cannot be used together")

    for opti , t,  req in options:
        if opti not in givenarg and req==True:
            print("Error"," ",opti," is a required arguement")
            noerror = 0



    # Checks if the values of the arguements given are appropriate or not
    for option , t , req in options:
        for opt , val in inputs :
            if option==opt and t==int and not val.isdigit():
                print("ERROR"," ",opt," is given a value of wrong data type")
                noerror=0

            if option==opt and t==str and val.isdigit():
                print("ERROR", " ", opt, " is given a value of wrong data type")
                noerror=0


    # Gives the output if no error is found
    if noerror != 0:
        jsonformat=json.dumps(dict(inputs))
        print(jsonformat)
