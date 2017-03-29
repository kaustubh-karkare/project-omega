import argparse
import socket
import json
import logging


BLOCK_SIZE = 255


class SumAndVerify:

    def __init__(self, client_socket, first_number, second_number):
        self.first_number = first_number
        self.second_number = second_number
        self.client_socket = client_socket

    def send_numbers_and_verify_sum(self):
        self.client_socket.send(
            json.JSONEncoder().encode(
                {
                    'first_number': self.first_number,
                    'second_number': self.second_number
                }
            )
        )
        self.response = json.JSONDecoder() \
            .decode(self.client_socket.recv(BLOCK_SIZE))
        if (
            self.first_number +
            self.second_number ==
            self.response['sum']
        ):
            logging.info(
                'The server gives the correct sum', self.response['sum'])
        else:
            logging.info('The server does not give the correct sum')


def connect_to_server(host, port):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_TCP
    )
    client_socket.connect((host, port))
    return client_socket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help='Server host')
    parser.add_argument('--port', type=int, required=True, help='Server port')
    parser.add_argument(
        '--first_number',
        '-num1',
        type=int,
        required=True,
        help='First number for summation'
    )
    parser.add_argument(
        '--second_number',
        '-num2',
        type=int,
        required=True,
        help='Second number for summation'
    )
    parsed_argument = parser.parse_args()
    client_socket = connect_to_server(
        parsed_argument.host, parsed_argument.port)

    SumAndVerify(
        client_socket,
        first_number=parsed_argument.first_number,
        second_number=parsed_argument.second_number
    ).send_numbers_and_verify_sum()

if __name__ == '__main__':
    main()
