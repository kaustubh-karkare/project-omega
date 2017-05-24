import socket
import sys
import logging
import argparse

CHUNK = 1024


class Client():

    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.socket = socket.socket()
        self.logger = logging.getLogger('Server')
        log_filename = 'Server.log'
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        FileHandler = logging.FileHandler(log_filename)
        self.logger.setLevel(logging.DEBUG)
        FileHandler.setFormatter(formatter)
        self.logger.addHandler(FileHandler)

    def send_and_verify(self, x, y):
        self.socket.connect((self.host, self.port))
        data_to_be_sent = str(x) + ' ' + str(y)
        self.socket.send(data_to_be_sent.encode())
        recieved_data = self.socket.recv(CHUNK)
        recieved_data = str(recieved_data.decode())
        data_to_be_sent = data_to_be_sent.split(' ')
        answer_of_sent_data = self.logic(x, y)
        self.socket.close()
        if not answer_of_sent_data == int(recieved_data):
            self.logger.info('error')
        else:
            self.logger.info('Result ' + recieved_data)


def main():
    add = lambda a, b: a + b
    multiply = lambda a, b: a * b
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help='Server host')
    parser.add_argument('--port', type=int, required=True, help='Server port')
    parser.add_argument('--num1', type=int, required=True, help='First number')
    parser.add_argument('--num2', type=int, required=True, help='Second number')
    parsed_arguments = parser.parse_args()
    host = parsed_arguments.host
    port = parsed_arguments.port
    x = parsed_arguments.num1
    y = parsed_arguments.num2
    client = Client(host, port, add)
    client.send_and_verify(x, y)


if __name__ == '__main__':
    main()
