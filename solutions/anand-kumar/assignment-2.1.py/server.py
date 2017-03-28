import argparse
import socket
import json
import time
import threading


class Server:

    def __init__(self, host, port):
        self.address = (host, port)

    def start_serving(self):
        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
        self.server_socket.bind(self.address)
        self.server_socket.listen(1)
        server_is_listening = True
        while server_is_listening:
            try:
                client_socket, client_address = self.server_socket.accept()
                ReceiveNumbersAndReturnSum(
                    client_socket, client_address).start()
            except KeyboardInterrupt:
                # ctrl+C was hit - server stopped listening
                server_is_listening = False
        self.server_socket.close()


class ReceiveNumbersAndReturnSum(threading.Thread):

    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        threading.Thread.__init__(self)

    def run(self):
        print('Client connection received from:'), self.client_address
        self.recieve_numbers_and_return_sum()

    def recieve_numbers_and_return_sum(self):
        self.numbers_to_sum = json.JSONDecoder().decode(
            self.client_socket.recv(255))
        self.first_number = self.numbers_to_sum['first_number']
        self.second_number = self.numbers_to_sum['second_number']
        time.sleep(2)
        self.client_socket.send(json.JSONEncoder().encode(
            {'sum': self.first_number + self.second_number}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help='Server host')
    parser.add_argument('--port', type=int, required=True, help='Server port')
    req_arguments = parser.parse_args()

    Server(host=req_arguments.host, port=req_arguments.port).start_serving()

if __name__ == '__main__':
    main()
