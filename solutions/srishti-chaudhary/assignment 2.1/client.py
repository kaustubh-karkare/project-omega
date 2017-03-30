#!/usr/bin/env python

import socket
import sys
import logging

# Creating TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#For maintaining a log of events
LOG_FILENAME = 'client.log'
logging.basicConfig(
  filename=LOG_FILENAME,
  level=logging.DEBUG,
)

# Connecting the socket to the port where the server is listening 
server_address = ('localhost', 10000)
logging.info('connecting to %s port %s' % server_address)
sock.connect(server_address, 10000)

first_number = int(sys.argv[1])
second_number = int(sys.argv[2])
client_sum = first_number + second_number
input_data = str(first_number) + ' ' + str(second_number)

try:
	# Sending data
	sock.sendall(input_data)
	server_sum = int(sock.recv(1024))
	if server_sum == client_sum:
		logging.info('Result Veified')
	else:
		logging.warning('Incorrect Result')
finally:
	logging.info('Closing socket')
	sock.close()
