import socket
import logging
import argparse
import threading
import time
from os import getcwd
from processhttprequest import ReceiveAndProcessRequest


class Server(threading.Thread):

    def __init__(self, host, port, base_directory):
        try:
            self.base_directory = base_directory
            self.server_socket = socket.socket()
            self.server_socket.bind((host, port))
            self.server_socket.settimeout(1)
        except:
            logging.error('Server socket could not be established')
            raise
        threading.Thread.__init__(self)

    def run(self):
        self.start_serving()

    def start_serving(self):
        self.server_socket.listen(1)
        self.server_listening = True
        while self.server_listening:
            try:
                self.client_socket, self.client_address = (
                    self.server_socket.accept()
                )
                ReceiveAndProcessRequest(
                    self.client_socket,
                    self.client_address,
                    self.base_directory
                )
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.server_listening = False

    def stop_serving(self):
        self.server_listening = False
        self.server_socket.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, type=str, help='Server Host')
    parser.add_argument('--port', required=True, type=int, help='Server port')
    parser.add_argument(
        '--base-directory',
        '-b',
        required=False,
        type=str,
        default=getcwd(),
        help='Base Directory'
    )
    parsed_argument = parser.parse_args()
    server = Server(
        host=parsed_argument.host,
        port=parsed_argument.port,
        base_directory=parsed_argument.base_directory,
    )
    server.start()
    time.sleep(180)
    server.stop_serving()

if __name__ == '__main__':
    main()
