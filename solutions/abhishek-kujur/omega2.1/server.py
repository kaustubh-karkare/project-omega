import socket
import threading


class server():
    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.socket_object = socket.socket()
        self.socket_object.bind((self.host, self.port))

    def listen(self):
        while True:
            self.socket_object.listen(2)
            connection, address = self.socket_object.accept()
            print(self.logic + "  " + str(address))
            operation = self.logic
            function = getattr(self, operation)
            thread = threading.Thread(target=function, args=(connection, address, ))
            thread.deamon = True
            thread.start()

    def add(self, connection, address):
        msg = "sum of :"
        print('connection from ', str(address))
        while True:
            recieved_data = connection.recv(1024)
            if not recieved_data:
                print("connection from " + str(address) + " is aborted")
                break
            data = str(recieved_data.decode()).split()
            x = int(data[0])
            y = int(data[1])
            sum_of_numbers = x + y
            data_to_be_sent = msg + str(sum_of_numbers)
            connection.send(data_to_be_sent.encode())
        connection.close()

    def mult(self, connection, address):
        msg = "product of :"
        print('connection from ', str(address))
        while True:
            recieved_data = connection.recv(1024)
            if not recieved_data:
                print("connection from " + str(address) + " is aborted")
                break
            data = str(recieved_data.decode()).split()
            x = int(data[0])
            y = int(data[1])
            sum_of_numbers = x * y
            data_to_be_sent = msg + str(sum_of_numbers)
            connection.send(data_to_be_sent.encode())
        connection.close()


def Main():
    s = server('127.0.0.1', 3000, 'mult')
    s.listen()


if __name__ == '__main__':
    Main()
