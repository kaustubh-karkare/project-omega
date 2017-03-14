# python assignment-1.py --key 123 --name abhijeet
import sys, json

total = len(sys.argv)
cmdarg = str(sys.argv)

if total == 1:
    print "Error: The '--key' argument is required, but missing from input."
elif total == 3 and str(sys.argv[1])=="--local" and str(sys.argv[2])=="--remote":
    print "Error: The --local and --remote arguments cannot be used together."
elif total ==3 :
    print json.dumps({'command': str(sys.argv[1]), 'sub-command': str(sys.argv[2])})
elif total == 4 and str(sys.argv[3])=="-v" :
    print json.dumps({'command': str(sys.argv[1]), 'sub-command': str(sys.argv[2]), 'Verbose':'True'})
elif str(sys.argv[1])=="--key" :
    try:
        value = int(sys.argv[2])
	if str(sys.argv[3])=="--name" and total == 5 :
	    print json.dumps({'--key': str(sys.argv[2]), '--name': str(sys.argv[4])})
    except ValueError:
        print "Error: The value for the '--key' argument must be a positive integer."
       
