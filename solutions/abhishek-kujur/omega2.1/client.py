import socket


def Main():
    host = '127.0.0.1'
    port = 3000
    connection = socket.socket()
    connection.connect((host, port))
    data_to_be_sent = input('->')
    while data_to_be_sent != '':
        connection.send(data_to_be_sent.encode())
        recieved_data = connection.recv(1024)
        recieved_data = str(recieved_data.decode())
        recieved_data = recieved_data.split(':')
        print(recieved_data[0] + data_to_be_sent + ' is ' + recieved_data[1])
        data_to_be_sent = input('->')
    connection.close()


if __name__ == '__main__':
    Main()
