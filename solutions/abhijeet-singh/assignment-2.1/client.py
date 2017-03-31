import socket
import sys
import cPickle
import argparse

class Client:

	def __init__(self, first_num, second_num, ip, port):
		self.ip = ip
		self.port = int(port)
		self.first_num = int(first_num)
		self.second_num = int(second_num)

	def main(self):
		host = socket.gethostbyname(socket.gethostname())
		client = socket.socket()
		client.connect((self.ip, self.port))
		data = (self.first_num, self.second_num)
		data_send = cPickle.dumps(data)
		client.send(data_send)
		result_server = int(client.recv(1024))
		result_client = self.first_num + self.second_num
		if (result_server == result_client):
			print "Result received ", result_server, " is correct"
		else:
			print "Result received ", result_server, " is incorrect"
		client.close()

if __name__ == '__main__':
	client_argument = argparse.ArgumentParser()
	client_argument.add_argument("-i","--ip", help = "Server's IP",
		 required = True)
	client_argument.add_argument("-p","--port", 
		help = "Server's Port for Connection", required = True)
	client_argument.add_argument("x", type = int, help = "First number")
	client_argument.add_argument("y", type = int, help = "Second number")
	client_argument = client_argument.parse_args()
	Client(client_argument.x, client_argument.y, client_argument.ip, 
		client_argument.port).main()
	
