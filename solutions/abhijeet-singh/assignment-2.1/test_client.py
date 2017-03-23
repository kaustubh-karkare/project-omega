import socket
import sys
import cPickle
import datetime

class Client(object):
	global client
	def __init__(self, data):
		self.data = data

	def callserver(self): 
		Host = socket.gethostbyname(socket.gethostname())
		self.client = socket.socket()
		self.client.connect(('127.0.1.1',1144))
		self.client.send(self.data)

	def receiveAndClose(self):
		self.client.recv(1024)
		self.client.close()

def test_client():
	data1 = (1, 9)
	data_send1 = cPickle.dumps(data1)
	data2 = (7, 3)
	data_send2 = cPickle.dumps(data2)
	data3 = (8, 2)
	data_send3 = cPickle.dumps(data3)
	client1 = Client(data_send1)
	client2 = Client(data_send2)
	client3 = Client(data_send3)
	a = datetime.datetime.now()
	client1.callserver()
	client2.callserver()
	client3.callserver()
	client1.receiveAndClose()
	client2.receiveAndClose()
	client3.receiveAndClose()
	b = datetime.datetime.now()
	c = b - a
	d = divmod(c.days * 86400 + c.seconds, 60)
	assert d[1] <= 3
	
