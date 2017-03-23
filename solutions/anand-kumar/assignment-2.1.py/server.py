# The server requires the server_host_name
# and the server_port_number number for its creation


import sys
import socket
import json
import time
import thread


class server:
    first_number = 0
    second_number = 0
    data_from_client = ''

    def __init__(self, client_socket_object):
        self.data_from_client = client_socket_object.recv(255)

    def extract_numbers_from_client_data(self):
        self.numbers_to_add = json.loads(self.data_from_client)
        self.first_number = self.numbers_to_add['first_number']
        self.second_number = self.numbers_to_add['second_number']

    def calculate_and_send_the_client_sum(self):
        self.sum_value = self.first_number + self.second_number
        self.sum_of_numbers = {'sum': self.sum_value}
        self.encode_sum_of_numbers = json.dumps(self.sum_of_numbers)
        time.sleep(2)
        return self.encode_sum_of_numbers


def thread_of_a_client(client_socket_object, client_address):
    print('Connection received from ', client_address)
    server_object = server(client_socket_object)
    server_object.extract_numbers_from_client_data()
    client_socket_object.send(
        server_object.calculate_and_send_the_client_sum())


def main():
    if (len(sys.argv) < 3):
        print('Insuffcient argument')
        sys.exit(2)
    server_socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host_name = sys.argv[1]
    server_port_number = int(sys.argv[2])
    server_socket_object.bind((server_host_name, server_port_number))
    server_socket_object.listen(5)
    while True:
        client_socket_object, client_address = server_socket_object.accept()
        thread.start_new_thread(thread_of_a_client,
                                (client_socket_object, client_address))
    server_socket_object.close()

if __name__ == '__main__':
    main()
