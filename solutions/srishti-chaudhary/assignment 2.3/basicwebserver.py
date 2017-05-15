#!/usr/bin/python

import socket  # Networking support
import signal  # Signal support (server shutdown on signal receive)
import time    # Current time
import os
import sys

# For maintaining a log of events
LOG_FILENAME = 'http.log'
logging.basicConfig(
  filename=LOG_FILENAME,
  level=logging.DEBUG,
)

class Server:
 """ Class describing a simple HTTP server objects."""

	def __init__(self, port = 80):
		""" Constructor """
		self.host = ''   # <-- works on all available network interfaces
		self.port = port

	def activate_server(self):
		""" Attempts to acquire the socket and launch the server """
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try: 
			logging.info("Launching HTTP server on ", self.host, ":",self.port)
			self.socket.bind((self.host, self.port))

		except Exception as e:
			logging.warning("Warning: Could not acquire port:",self.port,"\n")
			# store to user provided port locally for later (in case 8080 fails)
			user_port = self.port
			self.port = 8080

			try:
				logging.info("Launching HTTP server on ", self.host, ":",self.port)
				self.socket.bind((self.host, self.port))

			except Exception as e:
				logging.error("ERROR: Failed to acquire sockets for ports ", user_port, " and 8080. ")
				logging.info("Try running the Server in a privileged user mode.")
				self.shutdown()
				sys.exit(1)

		logging.info("Server successfully acquired the socket with port:", self.port)
		logging.info("Press Ctrl+C to shut down the server and exit.")
		self._wait_for_connections()

	def shutdown(self):
		""" Shut down the server """
		try:
			logging.info("Shutting down the server")
			s.socket.shutdown(socket.SHUT_RDWR)

		except Exception as e:
			logging.info("Warning: Could not shut down the socket. It may have been already closed",e)

	def _gen_headers(self,  code):	
		""" Generates HTTP response Headers. Omits the first line! """
		# determine response code
		h = ''
		if (code == 200):
			h = 'HTTP/1.1 200 OK\n'
		elif(code == 404):
			h = 'HTTP/1.1 404 Not Found\n'

		# write further headers
		current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		h += 'Date: ' + current_date +'\n'
		h += 'Server: Simple-Python-HTTP-Server\n'
		h += 'Connection: close\n\n'  # signal that the connection will be closed after completing the request

		return h
			
	def find_file(name, path):
		result = []
		flag = 0
		for root, dirs, files in os.walk(path):
			if name in files:
				flag = 1
				result.append(os.path.join(root, name))
		if flag==0
			for root, dirs, files in os.walk(path):
				for filename in files:
					filepath = os.path.join(root, filename)
					result.append(filepath)
	return result
		
	def _wait_for_connections(self):
		""" Main loop awaiting connections """
		while True:
			logging.info ("Awaiting New connection")
			self.socket.listen(3) # maximum number of queued connections
			conn, addr = self.socket.accept()
			logging.info("Got connection from:", addr)
			data = conn.recv(1024) 
			string = bytes.decode(data) # decode data to string

			# determine request method  (HEAD and GET are supported)
			request_method = string.split(' ')[0]
			logging.info ("Method: ", request_method)
			logging.info ("Request body: ", string)

			if (request_method == 'GET') | (request_method == 'HEAD'):
				# split on space "GET /file.html" -into-> ('GET','file.html',...)
				file_requested = string.split(' ')
				file_requested = file_requested[1] 

				# Check for URL arguments. Disregard them
				file_requested = file_requested.split('?')[0]  # disregard anything after '?'

				if os.path.isdir(file_requested): 
					files = find_file(‘index.html’, file_requested)

				if os.path.isfile(file_requested): 
				try:
					file_handler = open(file_requested,'rb')
					if (request_method == 'GET'):  #only read the file when GET
						response_content = file_handler.read() # read file content
						file_handler.close()
						response_headers = self._gen_headers( 200)

					except Exception as e: #in case file was not found, generate 404 page
						logging.warning("Warning, file not found. Serving response code 404\n", e)
						response_headers = self._gen_headers( 404)

				if (request_method == 'GET'):
					response_content = "<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"
					server_response =  response_headers.encode() # return headers for GET and HEAD
				if (request_method == 'GET'):
					server_response +=  response_content  # return additional conten for GET only
					
				conn.send(server_response)
				logging.info ("Closing connection with client")
				conn.close()

			else:
				logging.error("Unknown HTTP request method:", request_method)

def graceful_shutdown(sig, dummy):
	""" This function shuts down the server. It's triggered by SIGINT signal """
	s.shutdown() #shut down the server
	sys.exit(1)

# shut down on ctrl+c
signal.signal(signal.SIGINT, graceful_shutdown)

logging.info("Starting web server")
s = Server(80)  # construct server object
s.activate_server() # acquire the socket
