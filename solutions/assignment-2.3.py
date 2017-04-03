import threading
import socket
import time
import logging
import os
import argparse

class Server():
	
	def __init__(self, port):
		self.port = int(port)
		self.logger = logging.getLogger("Server")
		logging.basicConfig(level=logging.INFO)
		self.server_running = True

	# start the server on a thread
	def start(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ip = socket.gethostbyname(socket.gethostname())
		address = (ip, self.port)
		self.server.bind(address)
		self.server.listen(10)
		self.logger.info("Started listing on {} - {}".format(ip, self.port))
		thread = threading.Thread(target = self.server_thread)
		thread.start()

	# server start listining
	def server_thread(self):
		while self.server_running: 
			try:
				client, client_address = self.server.accept()
				self.logger.info("Got a connection from {} - {}".format(
					client_address[0], client_address[1]))
				thread = threading.Thread(
					target=self.request_handler, 
					args=(client, client_address)
				)
				thread.start()
			except EOFError:
				self.logger.warn("Nothing Received")
	
	# manages GET request from the client 
	def request_handler(self, client, client_address):
		data_received = client.recv(1024)
		# retriving information from the data received for the relative URL
		start_path = data_received.lower().find('get ')
		end_path = data_received.find('\r\n', start_path + 4)
		path = data_received[start_path + 4 : end_path]
		file_path = os.path.dirname(os.path.abspath(__file__)) + path
		# send file to client if present		
		if os.path.isfile(file_path):			
			client.send("HTTP/1.1 200 OK\r\n")
			send_file = open(file_path, "rb")
			l = send_file.read(1024)
			while True:
				client.send(l)
				l = send_file.read(1024)
				if not l:
					break
		elif os.path.isdir(file_path):			
			client.send("HTTP/1.1 200 OK\r\n")
			index_file_present = False
			file_list = os.listdir(file_path)
			# check for index.html in directory if present then send's the file
			if (list_item == 'index.html'):
				for list_item in file_list:
						index_file_present = True
						send_file = open(file_path+"/index.html", "rb")
						l = send_file.read(1024)
						while True:
							client.send(l)
							l = send_file.read(1024)
							if not l:
								break
			# if index.html in directory not present then return list of files
			if index_file_present == False:
				data = "File list \r\n"
				for list_item in file_list:
					data += list_item + "\r\n"
				client.send(data)
		else:
			# 404 error because of invalid relative URL
			client.send("HTTP/1.1 404 Not Found\r\n")
		self.logger.info("Result sent to {}".format(client_address[0]))
		client.close()

	def stop(self):
		self.server_running = False
		self.server.shutdown(socket.SHUT_RDWR)
		self.server.close()
		

if __name__ == '__main__':
	server_detail = argparse.ArgumentParser()
	server_detail.add_argument(
		"-p", 
		"--port", 
		help="port on which server will run", 
		required=True
	)
	server_detail.add_argument(
		"-t", 
		"--time", 		
		help="Time for server will be active in seconds", 
		default='150'
	)
	server = Server(server_detail.parse_args().port)
	server.start()
	time.sleep(float(server_detail.parse_args().time))
	server.stop()

