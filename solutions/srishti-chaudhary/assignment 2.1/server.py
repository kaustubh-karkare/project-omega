#!/usr/bin/env python

import socket
import sys
import time
import logging
import threading 

# For maintaining a log of events
LOG_FILENAME = 'server.log'
logging.basicConfig(
  filename=LOG_FILENAME,
  level=logging.DEBUG,
)

class ClientThread(threading.Thread):

        def __init__(self, ip, port, socket):
                threading.Thread.__init__(self)
                self.ip = ip
                self.port = port
                self.socket =socket
                logging.info('New thread started')

        def run(self):
                # Receiving data from client
		while True:
			data = connection.recv(1024)
			if not data: break
			logging.info('received %s' %data)
			time.sleep(2)
			data = data.split()
			server_sum = int(data[0]) + int(data[1])
			connection.send(str(server_sum))

# Creating TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Binding the socket to the port
server_address = ('localhost', 10000)
logging.info('starting server up on %s port %s' % server_address)
sock.bind(server_address)

# For multiple clients
threads = []

# For incoming connections
sock.listen(1)

while True:
	logging.info('waiting for connection')
	(connection, (ip, port)) = sock.accept()
	newthread = ClientThread(ip, port, connection)
	newthread.start()
	threads.append(newthread)

for t in threads
        t.join()
