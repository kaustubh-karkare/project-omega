import socket
import sys

CHUNK = 1024


class Client():
    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.socket = socket.socket()

    def send_and_verify(self, x, y):
        self.socket.connect((self.host, self.port))
        data_to_be_sent = x + ' ' + y
        self.socket.send(data_to_be_sent.encode())
        recieved_data = self.socket.recv(CHUNK)
        recieved_data = str(recieved_data.decode())
        data_to_be_sent = data_to_be_sent.split(' ')
        answer_of_sent_data = self.logic(int(x), int(y))
        self.socket.close()
        if not answer_of_sent_data == int(recieved_data):
            return 'error'
        else:
            return 'Result ' + recieved_data


def main():
    def add(a, b):
        result = a + b
        return result

    def multiply(a, b):
        result = a * b
        return result
    cli_arguments = sys.argv
    host_port = cli_arguments[1].split(':')
    host = host_port[0]
    port = int(host_port[1])
    x = cli_arguments[2]
    y = cli_arguments[3]
    client = Client(host, port, add)
    print(client.send_and_verify(x, y))


if __name__ == '__main__':
    main()
