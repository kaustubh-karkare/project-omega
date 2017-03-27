# The client is expected to enter the server host name, server port number,
# and the two numbers to be added as argument.

import sys
import socket
import json
import logging


class Client:

    def __init__(self, server_host, server_port, first_number, second_number):
        self.server_host = server_host
        self.server_port = server_port
        self.numbers_to_be_added = {
            'first_number': first_number,
            'second_number': second_number
        }
        self.create_client_socket()
        self.send_numbers_to_add()
        self.receive_sum_from_the_server()
        self.verify_received_sum()

    def create_client_socket(self):
        self.client_socket_object = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

    def send_numbers_to_add(self):
        self.client_socket_object.connect((self.server_host, self.server_port))
        self.client_socket_object.send(json.dumps(self.numbers_to_be_added))

    def receive_sum_from_the_server(self):
        self.sum_received = self.client_socket_object.recv(255)
        self.sum_received = json.loads(self.sum_received)

    def verify_received_sum(self):
        if (
                self.numbers_to_be_added['first_number'] +
                self.numbers_to_be_added['second_number'] ==
                self.sum_received['sum']):
            print('The server gives the correct sum: ',
                  self.sum_received['sum'])
        else:
            print('The server does not give the correct sum')


def main():
    if(len(sys.argv) < 5):
        logging.error('Argument(s) missing')
        sys.exit(2)
    Client(
        server_host=sys.argv[1],
        server_port=int(sys.argv[2]),
        first_number=int(sys.argv[3]),
        second_number=int(sys.argv[4]))

if __name__ == '__main__':
    main()
