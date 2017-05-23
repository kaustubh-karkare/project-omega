import socket
import threading
import logging


class Server():
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

    def listen(self):
        while True:
            self.socket.listen(2)
            connection, address = self.socket.accept()
            new_connection = self.new_connection
            thread = threading.Thread(target=new_connection, args=(connection, address, ))
            thread.start()

    def new_connection(self, connection, address):
        self.logger.info('connection from ' + str(address))
        self.logic(connection)


def main():
    def add(connection):
        recieved_data = connection.recv(1024)
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        result = x + y
        result = str(result)
        data_to_be_sent = result
        connection.send(data_to_be_sent.encode())
        connection.close()
        return

    def multiply(connection):
        recieved_data = connection.recv(1024)
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        result = x * y
        result = str(result)
        data_to_be_sent = result
        connection.send(data_to_be_sent.encode())
        connection.close()
        return
    server = Server('127.0.0.1', 3000, add)
    server.listen()


if __name__ == '__main__':
    main()
