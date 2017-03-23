# The server requires the server_host_name
# and the server_port_number number for its creation


import sys
import socket
import json
import time
import thread


class server:
    def __init__(self, data_from_client):
        numbers_to_add = json.loads(data_from_client)
        self.first_number = numbers_to_add['first_number']
        self.second_number = numbers_to_add['second_number']

    def calculate_sum(self):
        v = self.first_number + self.second_number
        sum_of_numbers = {'sum': v}
        encode_sum_of_numbers = json.dumps(sum_of_numbers)
        return encode_sum_of_numbers


def thread_of_a_client(client_socket_object, client_address):
    print('Connection received from ', client_address)
    data_from_client = client_socket_object.recv(255)
    server_object = server(data_from_client)
    time.sleep(2)
    server_evaluated_sum = server_object.calculate_sum()
    client_socket_object.send(server_evaluated_sum)

if (len(sys.argv) < 3):
    print('Insuffcient argument')
    sys.exit(2)
server_socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host_name = sys.argv[1]
server_port_number = int(sys.argv[2])
server_socket_object.bind((server_host_name, server_port_number))
server_socket_object.listen(5)
while True:
    client_socket_object, client_address = server_socket_object.accept()
    thread.start_new_thread(thread_of_a_client,
                            (client_socket_object, client_address))
server_socket_object.close()
