#!/usr/bin/env python3
"""Server to receive numbers and return sum using tcp socket connection."""

import socket  # For socket operations
import threading  # For Thread
import time  # For sleep

HOST = ''  # Any host
PORT = 54321  # Arbitrary port
DESIRED_OPERATION = sum  # Can be any function accepting tuple


def handle_client(client_socket, client_socket_address):
    """Find and send sum of numbers received from client_socket."""
    with client_socket:
        print('Connected to', client_socket_address)
        numbers_data = client_socket.recv(1024)
        time.sleep(2)
        numbers_str = str(numbers_data, 'UTF-8')
        numbers = tuple(int(num) for num in numbers_str.split())
        result = DESIRED_OPERATION(numbers)
        result_data_str = str(result)
        result_data = bytes(result_data_str, 'UTF-8')
        client_socket.sendall(result_data)


# Create server socket to accept connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
    mysocket.bind((HOST, PORT))
    mysocket.listen()
    while True:
        client_socket, client_socket_address = mysocket.accept()
        # Start a thread to handle the client
        threading.Thread(target=handle_client,
                         args=(client_socket, client_socket_address)
                         ).start()
