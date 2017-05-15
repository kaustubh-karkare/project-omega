import socket
import sys
import cPickle
import argparse
import logging

class Client():

	def __init__(
		self, 
		first_num, 
		second_num, 
		ip, 
		port
	):
		self.logger = logging.getLogger("Server")
		logging.basicConfig(level=logging.INFO)
		self.ip = ip
		self.port = int(port)
		self.first_num = int(first_num)
		self.second_num = int(second_num)
		self.client = socket.socket()
		self.client.connect((self.ip, self.port))

	def check_result(self):
		data = (self.first_num, self.second_num)
		data_send = cPickle.dumps(data)
		self.client.send(data_send)
		result_from_server = int(self.client.recv(1024))
		result_calculated_locally = self.first_num + self.second_num
		if (result_from_server == result_calculated_locally):
			result = "correct"
			
		else:
			result = "incorrect"
		self.logger.info(
			"Result received {} is {}".format(result_from_server, result)
		)
		self.client.close()

if __name__ == '__main__':
	client_argument = argparse.ArgumentParser()
	client_argument.add_argument(
		"-i", 
		"--ip", 
		help="Server's IP",
		required=True
	)
	client_argument.add_argument(
		"-p", 
		"--port", 
		help="Server's Port for Connection", 
		required=True
	)
	client_argument.add_argument("x", type=int, help="First number")
	client_argument.add_argument("y", type=int, help="Second number")
	client_argument = client_argument.parse_args()
	Client(
		client_argument.x, 
		client_argument.y, 
		client_argument.ip, 
		client_argument.port
	).check_result()	
