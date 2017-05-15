import socket


def Main():
    host = '127.0.0.1'
    port = 3000
    socket_object = socket.socket()
    socket_object.bind((host, port))
    socket_object.listen(1)
    connection, address = socket_object.accept()
    print('connection from ', str(address))
    while True:
        recieved_data = connection.recv(1024)
        if not recieved_data:
            break
        data = str(recieved_data.decode()).split()
        x = int(data[0])
        y = int(data[1])
        sum_of_numbers = x + y
        data_to_be_sent = str(sum_of_numbers)
        connection.send(data_to_be_sent.encode())
    connection.close()


if __name__ == '__main__':
    Main()
