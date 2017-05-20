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
            self.logger.info(self.host + ':' + str(self.port))
            function = self.function
            thread = threading.Thread(target=function, args=(connection, address, ))
            thread.start()

    def function(self, connection, address):
        self.logger.info('connection from ' + str(address))
        recieved_data = connection.recv(1024)
        if not recieved_data:
            self.logger.warning("connection from " + str(address) +
                                " is aborted")
            return
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        result = self.logic(x, y)
        data_to_be_sent = result
        connection.send(data_to_be_sent.encode())
        connection.close()


def main():
    def add(a, b):
        message = "sum:"
        result = a + b
        result = message + str(result)
        return result

    def multiply(a, b):
        message = "product:"
        result = a * b
        result = message + str(result)
        return result
    server = Server('127.0.0.1', 3000, multiply)
    server.listen()


if __name__ == '__main__':
    main()
