import socket
import sys
import cPickle

def main():
	total = len(sys.argv)
	cmdarg = str(sys.argv)

	Host = socket.gethostbyname(socket.gethostname())
	client = socket.socket()
	client.connect(('127.0.1.1',1236))
	data = (str(sys.argv[1]), str(sys.argv[2]))
	data_send = cPickle.dumps(data)
	client.send(data_send)
	result_server = int(client.recv(1024))
	result_client = int(str(sys.argv[1])) + int(str(sys.argv[2]))
	if(result_server == result_client):
		print "Result received ", result_server, " is correct"
		client.close()
	else:
		print "Result received ", result_server, " is incorrect"
		client.close()

if __name__ == '__main__':
	main()
	
