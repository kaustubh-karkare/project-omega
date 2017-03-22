# The server requires the server_host_name
# and the server_port_number number for its creation

import sys
import socket
import json
import time


if (len(sys.argv) < 3):
    print 'Insufficient argument'
    sys.exit(2)
server_socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host_name = sys.argv[1]
server_port_number = int(sys.argv[2])
server_socket_object.bind((server_host_name, server_port_number))
server_socket_object.listen(1)
while True:
    client_socket_object, client_address = server_socket_object.accept()
    print 'Connection received from ', client_address
    received_data = client_socket_object.recv(255)
    numbers_to_add = json.loads(received_data)
    summation = numbers_to_add['first_number'] + numbers_to_add['second_number']
    # Json object sum_of_numbers
    sum_of_numbers = {'sum': summation}
    encode_sum_of_numbers = json.dumps(sum_of_numbers)
    time.sleep(2)
    client_socket_object.send(encode_sum_of_numbers)
    client_socket_object.close()
server_socket_object.close()
