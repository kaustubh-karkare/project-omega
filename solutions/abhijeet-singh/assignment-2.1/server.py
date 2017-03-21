import socket
import time
import cPickle


def main():
	while True:
		try:
			client, clientAddress = server.accept()
			print "Got a connection from ", clientAddress[0], " - ", clientAddress[1]
			data_recv = client.recv(1024)
			data = cPickle.loads(data_recv)
			print "Received ", data, " from the client"
			time.sleep(2)
			sum_data = int(data[0]) + int(data[1])
			client.send(str(sum_data))
			print "Result sent"
		except EOFError:
			time.sleep(1)
			print "Nothing Received"

if __name__ == '__main__':
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ip = socket.gethostbyname(socket.gethostname())
	port = 1236
	address = (ip, port)
	server.bind(address)
	server.listen(1)
	print "Started listening on ", ip, " - ", port
	main()
