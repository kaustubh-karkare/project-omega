#! /usr/bin/env python

import socket
import sys
import time

# Creating TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Binding the socket to the port
server_address = ('localhost', 10000)

print >>sys.stderr, 'starting server up on %s port %s' % server_address
sock.bind(server_address)
# For incoming connections
sock.listen(1)

while True:
	print >>sys.stderr, 'waiting for connection'
	connection, client_address = sock.accept()
	try:
		print >>sys.stderr, 'connection from', client_address
		
		# Receiving data from client
		while True:
			data = connection.recv(1024)
			if not data: break
			print >>sys.stderr, 'received %s' %data
			time.sleep(2)
			data = data.split()
			server_sum = data[0] + data[1]
			connection.send(str(server_sum))
	finally:
		# Closing the connection
		connection.close()
