#!/usr/bin/env python3

"""
A Python script that takes command-line arguments and returns a JSON object

Arguments supported

1. List of short args and their long forms
2. List of required/mandatory args
3. List of args having a mandatory type
4. List of mutually exclusive args
5. One optional command with optional subcommand 

"""

import sys
import json
from collections import OrderedDict

acceptable = True

arg_dict = OrderedDict()  # list of input args
final_list = OrderedDict()    # list of output args

# add short arguments and their long versions here
list_of_comms = {
    "-h" : "--help", 
    "-N" : "--name", 
    "-R" : "--remote",
    "-L" : "--local",
    "-V" : "--verbose",
    "-k" : "--key",
}

# add long arguments which are required/mandatory
req_list_of_comms = [ "--key" ]

# add arguments here if they need to have a fixed data type
type_of_comms = {
    "--key" : int
}

# add mutually exclusive long arguments here
mutually_exclusive = {
    "--local" : "--remote"
}

p = sorted( list_of_comms.items(), key=lambda t: t[0] )
list_of_comms = OrderedDict( p )


# Check the validity of entered input
# s_full -> entire argument
# s1 -> argument part on the LHS of '='
# s2 -> argument part on the RHS of '='

def check(s_full, s1, s2):
    err = ""
    if ( len(s1) >= 2 and s1[0] == '-' and s1[1] != '-' ):    # for short input
        try:
            s1 = ( list_of_comms[s1] )                                # to long inp
            if ( s1 in type_of_comms.keys() ):
                try:
                    s2 = ( type_of_comms[s1] )(s2)
                except ValueError:                  # incorrect argument type
                    err1 = " The value for the "
                    err2 = " argument must be "
                    err = err1 + s1 + err2 + str( type_of_comms[s1] )
        except KeyError:
            err = " Unrecognized Argument " + s_full

    elif ( len(s1) > 2 and s1[0:2] == '--' ):                 # for long inputs
        found = False
        for key, val in list_of_comms.items():       # check argument validity
            if (s1 == val):
                found = True
                break
        if ( found == False ):
            err = " Unrecognized Argument "+ s_full
    else:
        err = " Unrecognized Argument "+ s_full
    if (s1 in type_of_comms.keys()):
        try:
            s2 = ( type_of_comms[s1] )(s2)
        except ValueError:                  # incorrect value type
            err1 = " The value for the "
            err2 = " argument must be "
            err = err1 + s1 + err2 + str( type_of_comms[s1] )
    return s1, s2, err


def print_help():
    print ( " The Following options are available : " )
    for key, value in list_of_comms.items():
        print(" " + key + "\t:\t" + value)


def take_args():
    i = 1
    while ( True ):
        try:
            s = str( sys.argv[i] )
            s = s.strip()
            pos = s.find( "=" )
            pos1 = s.find( "-" )
            
            if ( pos == -1 and pos1== -1 ):  # no '=' or '-'  -> positional arg
                temp_arg = { s : i }
                arg_dict.update( temp_arg )
            else:
                # '-' present but no '='-> short arg/ non value arg
                if (pos == -1):
                    s1 = s
                    s2 = "\*\*/*/"
                else:               # '=' present -> needs key, value pair
                    s1 = s[ : pos ]
                    s1 = s1.strip()
                    s2 = s[ pos+1 : ]
                    s2 = s2.strip()
                s1, s2, err_msg = check( s, s1, s2 )    # go to check function
                if ( err_msg == "" ):           # check validity by error msg
                    temp_arg = { s1 : s2 }
                    arg_dict.update( temp_arg )
                else:
                    print ( err_msg )
                    acceptable = False
                    print_help()
                    exit( 0 )
        except IndexError:
            return
        i += 1
	

take_args()
com_pos = None
subcom_pos = None

try:                                        # print help if -h/--help
    v = arg_dict[ '--help' ]
    print_help()
    exit( 0 )
except KeyError:
    None

for key, value in arg_dict.items():

    if (key[0:2]=='--'):            # check all input arguments

        # for all mutually exclusive args as keys
        if ( key in mutually_exclusive.keys() ):
            try:
                val = final_list[ key[ 2 : ] ]
                va = mutually_exclusive[ key ]
                if ( val == False ) :
                    pm1 = ' The "' + key + '" and the "' + va
                    pm2 = '" arguments cannot occur together '
                    print ( pm1 + pm2 )
                    acceptable = False
                    break
            except:
                temp_arg = { key[ 2 : ] : True }
                final_list.update( temp_arg )

        # for all mutually exclusive args as values
        elif ( key in ( list ( mutually_exclusive.values() ) ) ):
            va = 0
            for k, v in ( mutually_exclusive.items() ):
                if ( key == v ):
                    va = k
                    break;
            try:
                val = final_list[ va[ 2 : ] ]
                if (val == True):
                    pm1 = ' The "' + va + '" and the "' + key
                    pm2 = '" arguments cannot occur together '
                    print ( pm1 + pm2 )
                    acceptable = False
                    break
            except:
                temp_arg = { va[ 2 : ] : False}
                final_list.update( temp_arg )
        
        elif ( value == "\*\*/*/" ):        # args take true/false
            temp_arg = { key[ 2 : ] : True }
            final_list.update( temp_arg )
        else:
            temp_arg = { key[ 2 : ] : value }
            final_list.update( temp_arg )
    else:
        if ( com_pos == None ):         # check for command
            com_pos = value
            temp_arg = { "command" : key }
            final_list.update( temp_arg )
        elif( subcom_pos == None ):       # check for subcommand
            if ( com_pos == value - 1 ):
                subcom_pos = value
                temp_arg = { "subcommand" : key }
                final_list.update( temp_arg )
            else:
                print( " Unrecognized Argument " + key )
                acceptable = False
                break
        else:
            print( " Unrecognized Argument " + key)
            acceptable = False
            break

#check if all required args are present in input
for key in ( req_list_of_comms ):
    try:
        x = final_list[ key[ 2 : ]]
    except KeyError:
        print ("The " + key + " argument is required, but missing from input.")
        acceptable = False

if (acceptable == True):            # if no errors -> convert to JSON object
    json_obj = json.dumps( final_list )
    print ( json_obj )
else:
    print_help()
