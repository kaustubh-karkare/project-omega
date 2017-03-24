import socket
import thread
import time
import sys


# Class to calculate sum of the 2 numbers
class Addition(object):

    def __init__(self, express):
        self.express = express

    def answer(self):
        # Index of white space separating the 2 numbers
        index = self.express.index(' ')
        i = 0
        j = index + 1
        num1 = ''
        num2 = ''
        while (i < index):
            num1 += self.express[i]
            i = i + 1
        while (j > index and j < len(self.express)):
            num2 += self.express[j]
            j = j + 1
        add = int(num1) + int(num2)
        return add

    def multi_thread_implementation(client_socket_obj, client_addr):
        received_string = client_socket_obj.recv(1024)
        Addition_obj = Addition(received_string)
        print 'The client address is', client_addr
        time.sleep(2)
        server_evaluated_sum = Addition_obj.answer()
        print 'The sum calculated by the server is', server_evaluated_sum
        client_socket_obj.send(str(server_evaluated_sum))

# Create a socket object
server_socket_obj = socket.socket()
# Get local machine name
server_host = sys.argv[1]
# Reserve a port for your service
server_port = int(sys.argv[2])
# Binding server address to the socket
server_socket_obj.bind((server_host, server_port))
print 'Server code being executed.'
server_socket_obj.listen(5)
while True:
    client_socket_obj, client_addr = server_socket_obj.accept()
    # Implementing multi-threading
    try:
        thread.start_new_thread(multi_thread_implementation,
                                (client_socket_obj, client_addr))
    except:
        print 'Error: Unable to start thread'
server_socket_obj.close()
