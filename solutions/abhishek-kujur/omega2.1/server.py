import socket
import threading
import logging
import logging.handlers


class Server():
    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        self.logger = logging.getLogger('MyLogger')
        LOG_FILENAME = 'logfile'
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        FileHandler = logging.FileHandler(LOG_FILENAME)
        self.logger.setLevel(logging.DEBUG)
        FileHandler.setFormatter(formatter)
        self.logger.addHandler(FileHandler)

    def listen(self):
        while True:
            self.socket.listen(2)
            connection, address = self.socket.accept()
            self.logger.info(self.logic + "  " + self.host + ':' + str(self.port))
            operation = self.logic
            function = getattr(self, operation)
            thread = threading.Thread(target=function, args=(connection, address, ))
            thread.start()

    def add(self, connection, address):
        message = "sum:"
        self.logger.info('connection from ' + str(address))
        while True:
            recieved_data = connection.recv(1024)
            if not recieved_data:
                self.logger.warning("connection from " + str(address) +
                                    " is aborted")
                break
            data = str(recieved_data.decode()).split()
            x = int(data[0])
            y = int(data[1])
            sum_of_numbers = x + y
            data_to_be_sent = message + str(sum_of_numbers)
            connection.send(data_to_be_sent.encode())
        connection.close()

    def multiplication(self, connection, address):
        message = "product:"
        self.logger.info('connection from ' + str(address))
        while True:
            recieved_data = connection.recv(1024)
            if not recieved_data:
                self.logger.warning("connection from " + str(address) +
                                    " is aborted")
                break
            data = str(recieved_data.decode()).split()
            try:
                x = int(data[0])
                y = int(data[1])
                product_of_numbers = x * y
            except Exception:
                connection.close()
                break
            data_to_be_sent = message + str(product_of_numbers)
            connection.send(data_to_be_sent.encode())
        connection.close()


def Main():
    s = Server('127.0.0.1', 3000, 'multiplication')
    s.listen()


if __name__ == '__main__':
    Main()
