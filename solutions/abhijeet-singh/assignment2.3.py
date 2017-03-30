import threading
import socket
import time
import logging
import os

class Server():
	
	def connection(self, port):
		self.logger = logging.getLogger("Server")
		logging.basicConfig(level=logging.INFO)
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ip = socket.gethostbyname(socket.gethostname())
		address = (ip, int(port))
		server.bind(address)
		server.listen(10)
		self.logger.info("Started listing on {} - {}".format(ip, port))
		while True: 
			try:
				client, client_address = server.accept()
				self.logger.info("Got a connection from {} - {}".format(client_address[0], client_address[1]))
				thread = threading.Thread(target=self.request_handler, args=(client, client_address))
				thread.start()
			except EOFError:
				self.logger.warn("Nothing Received")
	
	def request_handler(self, client, client_address):
		data_recv = client.recv(1024)
		# retriving information from get method
		start_path = data_recv.lower().find('get ')
		end_path = data_recv.find('\r\n', start_path + 4)
		path = data_recv[start_path + 4 : end_path]
		file_path = os.path.dirname(os.path.abspath(__file__)) + path
		if os.path.isfile(file_path):
			# send file to client
			send_file = open(file_path, "rb")
			l = send_file.read(1024)
			while True:
				client.send(l)
				l = send_file.read(1024)
				if not l:
					break
		elif os.path.isdir(file_path):
			is_index = False
			file_list = os.listdir(file_path)
			# check for index.html in dir if present then send
			for list_item in file_list:
				if(list_item == 'index.html'):
					is_index = True
					send_file = open(file_path+"/index.html", "rb")
					l = send_file.read(1024)
					while True:
						client.send(l)
						l = send_file.read(1024)
						if not l:
							break
			# if index.html in dir not present return list
			if is_index == False:
				data = "File list \r\n"
				for list_item in file_list:
					data += list_item + "\r\n"
				client.send(data)
		else:
			# 404 error
			client.send("HTTP/1.1 404 Not Found")
		self.logger.info("Result sent to {}".format(client_address[0]))
		client.close()
		

if __name__ == '__main__':
	port = raw_input("Enter port on which server will listen ")
	Server().connection(port)
