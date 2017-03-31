import socket
import os
import time

class Server:
	""" This class describes the simple http server objects """ 
	def __init__(self , port=3000):
		self.host = "127.0.0.1"
		self.port = port
		self.rootDir = 'www'

	def startServer(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try: #chek weather the _init_ port is available or not
			print("Server started on port " + str(self.port))
			self.socket.bind((self.host, self.port))
		except:
			print("The required port is unavailable please try other port")
			exit(1)
		self.waitForConnection()

	def genrateHeader(self, code):
		"""Genrates http response header"""
		header = ""
		if(code == 200):
			header = 'HTTP/1.1 200 OK\n'
		elif(code == 404):
			header = 'HTTP/1.1 404 Not Found\n'

		current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	    	header += 'Date: ' + current_date +'\n'
                header += 'Server: Simple-Python-HTTP-Server\n'
		header += 'Connection: close\n\n'  # signal that the conection wil be closed after complting the request
		return header

	def waitForConnection(self):
		#Loop that waits for the connection
		while True:
			print("Waiting for client to join")
			self.socket.listen(3)
			conn, addr = self.socket.accept()
			# addr:-client address
			print("Connected by " + str(addr))

			data = conn.recv(1024)
			string = bytes.decode(data)

			#get request type
			method = string.split(' ')[0]

			if(method == 'GET'):
				file = string.split(' ')[1]

				file =  self.rootDir + file #

				
				isThereIndexFile = True #key to chek weather there is index file or not in the requested folde
				#chek weather the request is directory or file
				if(os.path.isdir(file)==True):
					listOfFiles = os.listdir(file)
					file = file + "/index.html"
					#chek for the exsistence of index file in the folder
					if(os.path.isfile(file)==False):
						isThereIndexFile = False

				try:
					handle = open(file,'rb')
					if(method == 'GET'):
						response = handle.read()
					handle.close()
					responseHeader = self.genrateHeader( 200)
				except:
					responseHeader = self.genrateHeader( 404)
					if(isThereIndexFile == False):
						#if there is no index file inside the folder
						#print all the files in it
						response = ""
						transferredList = 0
						while len(listOfFiles) > transferredList:
							response = response + listOfFiles[transferredList] +"\n"
							transferredList = transferredList + 1

						
					else:
						#if the request if file and it is not found send 404 error
						response = "404 error"
					

				serverResponse = responseHeader.encode() #return header for get
				if(method == 'GET'):
					serverResponse = serverResponse + response
				conn.send(serverResponse)
				print("Connection with client closed")
				conn.close()
			else:
				print("Not a GET HTTP request")

print("Starting webserver")
s = Server(3000)
s.startServer()





