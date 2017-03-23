# The client side code requires the server host name,
# port number and the arguments to calucalte the sum

import sys
import socket
import json


if (len(sys.argv) < 5):
    print('Insufficient argument')
    sys.exit(2)
client_socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])
# Json object numbers_to_be_added
numbers_to_be_added = {
    'first_number': int(sys.argv[3]),
    'second_number': int(sys.argv[4])
}
client_socket_object.connect((host, port))
client_socket_object.send(json.dumps(numbers_to_be_added))
data_from_server = client_socket_object.recv(255)
sum_of_numbers = json.loads(data_from_server)
if (numbers_to_be_added['first_number'] +
        numbers_to_be_added['second_number'] == sum_of_numbers['sum']):
    print('The server gives the correct sum: ', sum_of_numbers['sum'])
else:
    print('The server gives an incorrect sum')
client_socket_object.close()
