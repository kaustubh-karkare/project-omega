# The client side code requires the server host name,
# port number and the arguments to calucalte the sum

import sys
import socket
import json


class client:

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket_object = socket.socket(socket.AF_INET,
                                                  socket.SOCK_STREAM)

    def data_to_send_to_server(self, first_number, second_number):
        self.numbers_to_be_added = {
            'first_number': first_number,
            'second_number': second_number
        }

    def data_exchange_from_server(self):
        self.client_socket_object.connect((self.server_host, self.server_port))
        self.client_socket_object.send(json.dumps(self.numbers_to_be_added))
        self.data_from_server = self.client_socket_object.recv(255)
        self.sum_of_numbers = json.loads(self.data_from_server)

    def check_server_and_client_result(self):
        if (self.numbers_to_be_added['first_number'] +
                self.numbers_to_be_added['second_number'] ==
                self.sum_of_numbers['sum']):
            print('The server gives the correct sum: ',
                  self.sum_of_numbers['sum'])
        else:
            print('The server gives an incorrect sum')


def main():
    if(len(sys.argv) < 5):
        print('Insufficient argument')
        sys.exit(2)
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    client_object = client(server_host, server_port)
    client_object.data_to_send_to_server(int(sys.argv[3]), int(sys.argv[4]))
    client_object.data_exchange_from_server()
    client_object.check_server_and_client_result()

if __name__ == '__main__':
    main()
