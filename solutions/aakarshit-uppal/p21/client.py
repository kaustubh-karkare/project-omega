"""."""
import socket
import sys
# import pickle

HOST = socket.gethostname()
PORT = 54321

numbers = (int(sys.argv[1]), int(sys.argv[2]))
numbers_data_str = str(numbers)
numbers_data = bytes(numbers_data_str, 'UTF-8')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
    mysocket.connect((HOST, PORT))
    mysocket.sendall(numbers_data)
    result_data = mysocket.recv(1024)
    result_data_str = str(result_data, 'UTF-8')
    result = int(result_data_str)

print('Sum is', result)
