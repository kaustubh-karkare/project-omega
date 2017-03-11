#!/usr/bin/env python3

"""
A Python script that takes command-line arguments and returns a JSON object

Arguments supported

1. key -> Required positive integer
2. name -> String argument (Optional)
3. verbose -> Optional
4. local -> Optional, cannot be present with remote
5. remote -> Optional, cannot be present with local
6. command -> Optional
7. subcommand -> Optional

"""

import sys
import json
from collections import OrderedDict

acceptable = True

arg_dict=OrderedDict()  #list of input args
final_list=OrderedDict()    #list of output args
#list of short and long args
list_of_comms={
                "-h":"--help", 
                "-N":"--name", 
                "-R":"--remote",
                "-L":"--local",
                "-V":"--verbose",
                "-k":"--key",
        }

list_of_comms=OrderedDict(sorted(list_of_comms.items(), key=lambda t: t[0]))


#Check the validity of entered input

def check(s, s1, s2):
    err=""
    if (len(s1)>=2 and s1[0] == '-' and s1[1]!='-'):    #inputs of short type "-N"
        try:
            s1 = (list_of_comms[s1])                            # convert to inputs of long type "--name"
            if (s1 == "--key"):                                         #check if "--key" >=0
                try:
                    s2 = int(s2)
                    if (s2<0):
                        err="The value for the '--key' argument must be a positive integer."
                except ValueError:
                    err="The value for the '--key' argument must be a positive integer."
        except KeyError:
            err="Unrecognized Argument "+s

    elif (len(s1)>2 and s1[0:2]=='--'):                 #inputs of long type "--name"
        found=False
        for key,val in list_of_comms.items():       #search if input is in key
            if (s1 == val):
                found = True
                break
        if (found==False):
            err="Unrecognized Argument "+s
    if (s1 == "--key"):                                             #again check if "--key" >= 0
        try:
            s2 = int(s2)
            if (s2<0):
                err="The value for the '--key' argument must be a positive integer."
        except ValueError:
            err="The value for the '--key' argument must be a positive integer."
    return s1, s2, err


def print_help():                                               #prints help menu
    print ("The Following options are available : ")
    for key,value in list_of_comms.items():
        print(key+"\t:\t"+value)


def take_args():                                        # routine to parse input
    i = 1
    while (True):
        try:
            s = str(sys.argv[i])
            s = s.strip()
            pos = s.find("=")
            pos1 = s.find("-")
            if (pos == -1 and pos1==-1):            #Both "=" and "-" not present - maybe command or subcommand
                temp_arg = {s : i}
                arg_dict.update(temp_arg)
            else:
                if (pos == -1):                                 #"=" not present but "-" present -> maybe short arg or local/remote, no key,value pair needed
                    s1 = s
                    s2 = ""
                else:                                               #"=" present -> needs key, value pair
                    s1 = s[:pos]
                    s1 = s1.strip()
                    s2 = s[pos+1:]
                    s2 = s2.strip()
                s1, s2, err_mssg = check(s, s1, s2)     #go to check function
                #print (s1+str(s2)+err_mssg)
                if (err_mssg == ""):                        #check validity through returned error message
                    temp_arg = {s1 : s2}
                    arg_dict.update(temp_arg)
                else:
                    print(err_mssg)
                    acceptable = False
                    print_help()
                    exit(0)
        except IndexError:
            return
        i+=1
	

take_args()
com_pos = None
subcom_pos = None

try:                                        #print help if -h/--help
    v = arg_dict['--help']
    print_help()
    exit(0)
except KeyError:
    None

for key, value in arg_dict.items():
    if (key[0:2]=='--'):                        # check all input arguments
        if (key == '--local'):                  # checks for local and remote
            try:
                val = final_list['local']
                if (val ==False):
                    print('The "--local" and "--remote" arguments cannot be used together.')
                    acceptable = False
                    break
            except:
                temp_arg = {"local":True}
                final_list.update(temp_arg)
        elif (key == '--remote'):               # checks for local and remote
            try:
                val = final_list['local']
                if (val == True):
                    print('The "--local" and "--remote" arguments cannot be used together.')
                    acceptable = False
                    break
            except:
                temp_arg = {"local":False}
                final_list.update(temp_arg)
        elif (key == '--verbose'):          # verbose
            temp_arg = {key[2:] : True}
            final_list.update(temp_arg)
        elif (key == '--name' and value ==''):
            print("Name must have a value")
            acceptable = False
            break
        else:                                       #add in final_list
            temp_arg = {key[2:] : value}
            final_list.update(temp_arg)
    else:
        if (com_pos == None):           #check for command
            com_pos = value
            temp_arg = {"command":key}
            final_list.update(temp_arg)
        elif(subcom_pos == None):       #check for subcommand
            if (com_pos == value - 1):
                subcom_pos = value
                temp_arg = {"subcommand":key}
                final_list.update(temp_arg)
            else:
                print("Unrecognized Argument "+key)
                acceptable = False
                break
        else:
            print("Unrecognized Argument "+key)
            acceptable = False
            break
try:                                                    #check if --key present
    v = final_list['key']
except KeyError:
    print ("The '--key' argument is required, but missing from input.")
    acceptable = False
if (acceptable == True):            #if no errors -> convert to JSON object
    json_obj = json.dumps(final_list)
    print (json_obj)
else:
    print_help()
