#!/usr/bin/env python3
"""Client to send numbers and receive sum using tcp socket connection."""

import socket  # For socket operations
import sys  # For argv

HOST = socket.gethostbyname(socket.gethostname())  # Get current host
PORT = 54321  # Port number of server
DESIRED_OPERATION = sum  # Can be any function accepting tuple

# Extract and process numbers from command line
num1 = int(sys.argv[1])
num2 = int(sys.argv[2])
numbers = (num1, num2)
numbers_str = str(num1) + ' ' + str(num2)
numbers_data = bytes(numbers_str, 'UTF-8')

# Connect to server to send numbers and receive result
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
    mysocket.connect((HOST, PORT))
    mysocket.sendall(numbers_data)
    result_data = mysocket.recv(1024)
    result_data_str = str(result_data, 'UTF-8')
    result = int(result_data_str)

# Verify result
assert result == DESIRED_OPERATION(numbers)
