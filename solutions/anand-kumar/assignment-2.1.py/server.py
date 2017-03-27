# The server requires the server_host name
# and the server port number number as arguments.

import logging
import sys
import socket
import json
import time
import threading


class Server:

        def __init__(self, server_host, server_port):
            self.address = (server_host, server_port)

        def start_surveying(self):
            self.server_socket = socket.socket()
            self.server_socket.bind(self.address)
            self.server_socket.listen(1)
            while True:
                client_socket, client_address = self.server_socket.accept()
                ClientThread(client_socket, client_address).start()
            self.server_socket.close()


class ClientThread(threading.Thread):

    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        threading.Thread.__init__(self)

    def run(self):
        print('Client connection received from:'), self.client_address
        self.recieve_numbers_to_sum()
        self.decode_received_data()
        self.calculate_the_sum()
        self.encode_and_send_sum()

    def recieve_numbers_to_sum(self):
        self.numbers_to_sum = self.client_socket.recv(255)

    def decode_received_data(self):
        self.numbers_to_sum = json.loads(self.numbers_to_sum)
        self.first_number = self.numbers_to_sum['first_number']
        self.second_number = self.numbers_to_sum['second_number']

    def calculate_the_sum(self):
        self.sum_of_numbers = {'sum': self.first_number + self.second_number}
        time.sleep(2)

    def encode_and_send_sum(self):
        self.encode_sum_of_numbers = json.dumps(self.sum_of_numbers)
        self.client_socket.send(self.encode_sum_of_numbers)


def main():
    if (len(sys.argv) < 3):
        logging.error('Host name or port number(or both) missing')
        exit(2)
    Server(
        server_host=sys.argv[1],
        server_port=int(sys.argv[2])).start_surveying()

if __name__ == '__main__':
    main()
