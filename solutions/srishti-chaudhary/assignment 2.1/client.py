#! /usr/bin/env python

import socket
import sys

# Creating TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecting the socket to the port where the server is listening 
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

def calculate_sum():
	first_number = int(sys.argv[1])
	second_number = int(sys.srgv[2])
	result = first_number + second_number
	return result

try:
	# Sending data
	sock.sendall(sys.argv[1] + ' ' + sys.argv[2])
	server_sum = int(sock.recv(1024))
	client_sum = calculate_sum()
	if server_sum == client_sum:
		print >>sys.stderr, 'Result Verifired'
	else:
		print >>sys.stderr, 'Incorrect Result'
finally:
	print >>sys.stderr, 'Closing socket'
	sock.close()

		
