import socket
import logging
import argparse
import concurrent.futures
import threading
import time
from processhttprequest import ReceiveAndProcessRequest


class Server(threading.Thread):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        threading.Thread.__init__(self)

    def run(self):
        self.start_serving()

    def start_serving(self):
        try:
            server_socket = socket.socket()
            server_socket.bind((self.host, self.port))
            server_socket.settimeout(1)
            server_socket.listen(1)
        except:
            logging.error('Server socket could not be established')
            raise
        self.server_listening = True
        client_connections = []
        # Assuming maximum simultaneous request to be 5
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        while self.server_listening:
            try:
                client_socket, client_address = server_socket.accept()
                client_connections.append(
                    executor.submit(
                        ReceiveAndProcessRequest,
                        client_socket,
                        client_address,
                    )
                )
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.server_listening = False
        concurrent.futures.wait(client_connections)
        server_socket.close()

    def stop_serving(self):
        self.server_listening = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, type=str, help='Server Host')
    parser.add_argument('--port', required=True, type=int, help='Server port')
    parsed_argument = parser.parse_args()
    server = Server(host=parsed_argument.host, port=parsed_argument.port)
    server.start()
    time.sleep(30)
    server.stop_serving()

if __name__ == '__main__':
    main()
