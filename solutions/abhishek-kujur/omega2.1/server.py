import socket
from threading import Thread
import logging
import time

CHUNK = 1024


class Server(Thread):

    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        self.logger = logging.getLogger('Server')
        log_filename = 'Server.log'
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        FileHandler = logging.FileHandler(log_filename)
        self.logger.setLevel(logging.DEBUG)
        FileHandler.setFormatter(formatter)
        self.logger.addHandler(FileHandler)
        Thread.__init__(self)

    def run(self):
        self.server_listen = True
        self.__listen()

    def __listen(self):
        while self.server_listen:
            self.socket.listen(2)
            connection, address = self.socket.accept()
            thread = Thread(target=self.__new_connection,
                            args=(connection, address, ))
            thread.start()

    def __new_connection(self, connection, address):
        self.logger.info('connection from ' + str(address))
        self.logic(connection)

    def stop(self):
        self.server_listen = False
        return


def main():
    def add(connection):
        recieved_data = connection.recv(CHUNK)
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        result = x + y
        result = str(result)
        data_to_be_sent = result
        connection.send(data_to_be_sent.encode())
        connection.close()

    def multiply(connection):
        recieved_data = connection.recv(CHUNK)
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        result = x * y
        result = str(result)
        data_to_be_sent = result
        connection.send(data_to_be_sent.encode())
        connection.close()
    server = Server('127.0.0.1', 5000, add)
    server.start()
    time.sleep(5)
    server.stop()


if __name__ == '__main__':
    main()
