import socket
import sys


# Create a socket object
client_socket_obj = socket.socket()
# Get local machine name
client_host = sys.argv[1]
# Reserve a port for your service
client_port = int(sys.argv[2])
num1 = int(sys.argv[3])
num2 = int(sys.argv[4])
add = str(num1 + num2)
print 'The sum calculated by the client is', add
# The client object is connecting to the given address
client_socket_obj.connect((client_host, client_port))
print 'Connection to the server is made.'
# The expression to be sent to the server is evaluated
expression = str(num1) + ' ' + str(num2)
client_socket_obj.send(expression)
valuated_expression = client_socket_obj.recv(1024)
if evaluated_expression == add:
    print 'Sum calculated by server and client is the same.'
    print 'VERIFIED.'
else:
    print 'Sum calculated by server and client is not the same.'
    print 'NOT VERIFIED.'
