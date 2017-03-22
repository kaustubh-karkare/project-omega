import socket  
import time  


# Create a socket object
server_socket_obj = socket.socket()
# Get local machine name
server_host = socket.gethostname()  
# Reserve a port for your service
server_port = 1011 
# Binding server address to the socket
server_socket_obj.bind((server_host, server_port))
print 'Server code being executed.'
server_socket_obj.listen(5)
while True:
    # Stores the sum of the 2 numbers
    add = 0
    # Stores each individual number
    num_as_string = ''  
    client_obj, client_addr = server_socket_obj.accept()
    # Data received from the client
    received_string = client_obj.recv(1024)  
    received_string = received_string + ' '
    for character in received_string:
        if character != ' ':
            num_as_string += character
        else:
            add = add + int(num_as_string)
            num_as_string = ''
    time.sleep(2)
    print 'The sum calculated by the server is',add
    client_obj.send(str(add))
    client_obj.close()
