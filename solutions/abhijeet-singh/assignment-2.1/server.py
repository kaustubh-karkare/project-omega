import threading
import socket
import time
import cPickle
import logging

class Server():
	
	def connection(self, port):
		self.logger = logging.getLogger("Server")
		logging.basicConfig(level=logging.INFO)
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ip = socket.gethostbyname(socket.gethostname())
		address = (ip, int(port))
		server.bind(address)
		server.listen(1)
		self.logger.info("Started listing on {} - {}".format(ip, port))
		while True: 
			try:
				client, client_address = server.accept()
				self.logger.info("Got a connection from {} - {}".format(client_address[0], client_address[1]))
				thread = threading.Thread(target=self.addition_thread, args=(client, client_address))
				thread.start()
			except EOFError:
				time.sleep(2)
				self.logger.warn("Nothing Received")
	
	def addition_thread(self, client, client_address):
		data_recv = client.recv(1024)
		data = cPickle.loads(data_recv)
		self.logger.info("Received {} from client".format(data))
		time.sleep(2)
		sum_data = int(data[0]) + int(data[1])
		client.send(str(sum_data))
		self.logger.info("Result sent to {}".format(client_address[0]))
		

if __name__ == '__main__':
	port = raw_input("Enter port on which server will listen ")
	Server().connection(port)
