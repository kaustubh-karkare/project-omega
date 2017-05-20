import socket
import sys

chunk = 1024


def main(logic):
    input_string = sys.argv
    input_string = input_string[1].split(':')
    host = input_string[0]
    port = int(input_string[1])
    connection = socket.socket()
    connection.connect((host, port))
    data_to_be_sent = input('->')
    connection.send(data_to_be_sent.encode())
    recieved_data = connection.recv(chunk)
    recieved_data = str(recieved_data.decode())
    recieved_data = recieved_data.split(':')
    data_to_be_sent = data_to_be_sent.split(' ')
    answer_of_sent_data = logic(int(data_to_be_sent[0]), int(data_to_be_sent[1]))
    if not answer_of_sent_data == int(recieved_data[1]):
        print('error')
    else:
        print(recieved_data[0] + ' of ' + data_to_be_sent[0]
              + ' & ' + data_to_be_sent[1] + ' is ' + recieved_data[1])
    connection.close()


if __name__ == '__main__':
    def add(a, b):
        result = a + b
        return result

    def multiply(a, b):
        result = a * b
        return result
    main(multiply)
