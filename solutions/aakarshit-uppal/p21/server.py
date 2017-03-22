#!/usr/bin/env python3
"""."""
import socket
import ast

HOST = ''
PORT = 54321

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
    mysocket.bind((HOST, PORT))
    mysocket.listen()
    while True:
        client_socket, client_socket_address = mysocket.accept()
        with client_socket:
            print('Connected to' + str(client_socket_address))
            while True:
                numbers_data = client_socket.recv(1024)
                if not numbers_data:
                    break
                numbers_data_str = str(numbers_data, 'UTF-8')
                numbers = ast.literal_eval(numbers_data_str)
                result = sum(numbers)
                result_data_str = str(result)
                result_data = bytes(result_data_str, 'UTF-8')
                client_socket.sendall(result_data)
