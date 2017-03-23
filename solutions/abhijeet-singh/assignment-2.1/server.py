import threading
import socket
import time
import cPickle

class server() :
	lock = threading.Lock()
	def connection(self) :
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ip = socket.gethostbyname(socket.gethostname())
		port = 1144
		address = (ip, port)
		server.bind(address)
		server.listen(1)
		print "Started listening on ", ip, " - ", port
		while True : 
			try :
				client, clientAddress = server.accept()
				self.lock.acquire()
				print "Got a connection from ", clientAddress[0], " - ", clientAddress[1]
				thread = threading.Thread(target=self.additionThread, args=(client, clientAddress))
				thread.start()
				self.lock.release()
			except EOFError :
				time.sleep(2)
				print "Nothing Received"
	
	def additionThread(self, client, clientAddress) :
		self.lock.acquire()
		data_recv = client.recv(1024)
		data = cPickle.loads(data_recv)
		print "Received ", data, " from the client"
		self.lock.release()
		time.sleep(2)
		self.lock.acquire()
		sum_data = int(data[0]) + int(data[1])
		client.send(str(sum_data))
		print "Result sent to ", clientAddress[0]
		self.lock.release()
		

if __name__ == '__main__' :
	server().connection()
