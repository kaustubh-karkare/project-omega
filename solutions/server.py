import os
import socket

from handleclient import HandleClient


class Server:

    def __init__(self, host, port, document_root):
        os.chdir(document_root)
        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )
        self.server_socket.bind((host, port))
        self.server_socket.settimeout(1)
        self.server_listening = False

    def start_serving(self):
        self.server_listening = True
        self.server_socket.listen(5)
        while self.server_listening:
            try:
                client_socket, client_address = self.server_socket.accept()
                HandleClient(client_socket, client_address,).start()
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                self.server_listening = False
                self.server_socket.close()

    def stop_serving(self):
        self.server_listening = False
        self.server_socket.close()
