import threading
import socket
import time
import cPickle
import logging
import argparse

class Server():
	
	def __init__(self, ip, port):
		self.port = int(port)
		self.ip = ip
		self.server_running = True
		self.logger = logging.getLogger("Server")
		logging.basicConfig(level=logging.INFO)
	
	def start(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		address = (self.ip, self.port)
		self.server.bind(address)
		self.server.listen(10)
		self.logger.info("Started listing on {} - {}"
			.format(self.ip, self.port))
		thread = threading.Thread(target = self.server_thread)
		thread.start()
		
	def server_thread(self):
		while self.server_running: 
			try:
				client_connection, client_address = self.server.accept()
				self.logger.info("Got a connection from {} - {}".format(
					client_address[0], client_address[1]))
				thread = threading.Thread(target = self.addition_thread, 
					args = (client_connection, client_address))
				thread.start()
			except EOFError:
				self.logger.warn("Nothing Received")
	
	def addition_thread(self, client_connection, client_address):
		data_received = client_connection.recv(1024)
		data = cPickle.loads(data_received)
		self.logger.info("Received {} from client".format(data))
		time.sleep(2)
		sum_data = int(data[0]) + int(data[1])
		client_connection.send(str(sum_data))
		self.logger.info("Result sent to {}".format(client_address[0]))

	def stop(self):
		self.server_running = False
		self.server.shutdown(socket.SHUT_RDWR)
		self.server.close()


if __name__ == '__main__':
	server_detail = argparse.ArgumentParser()
	server_detail.add_argument(
		"-i", 
		"--ip", 
		help="IP in which server wil run", 
		default='127.0.0.1'
		)
	server_detail.add_argument(
		"-p", 
		"--port", 
		help="Server's Port listening Connection", 
		required=True
		)
	server_detail.add_argument(
		"-t", 
		"--time", 
		help="Time for server will be active in seconds", 
		default='150'
		)
	server_detail = server_detail.parse_args()
	server = Server(server_detail.ip, server_detail.port)
	server.start()
	time.sleep(float(server_detail.time))
	server.stop()

