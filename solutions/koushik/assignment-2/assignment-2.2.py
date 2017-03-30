import socket
import sys
import logging
import argparse
import threading
import time
from urlparse import urlparse
from mimetools import Message
from StringIO import StringIO
import os
LEVELS = {'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}
THREAD_COUNT = 4

class Client (threading.Thread):
    def __init__(self, thread_id, hostname, 
    			 port, path, start_range, end_range):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.hostname = hostname
        self.port = port
        self.path = path
        self.start_range = start_range
        self.end_range = end_range

    def run(self):
		logging.info("[Start: %s]", self.start_range)
		logging.info("[End: %s]", self.end_range)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((self.hostname, self.port))
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)
		# Send HEAD Request to fetch Headers  
		sock.send("GET %s HTTP/1.1\r\nHost: %s\r\nRange: bytes=%s-%s\r\nConnection: close\r\n\r\n"
			% (self.path, self.hostname, self.start_range, self.end_range))
		data = sock.recv(512)
		recv = ""
		while len(data):
			recv = recv + data
			data = sock.recv(512)
		# Write to Partfile after removing Headers
		with open('partfile'+str(self.thread_id),'w') as f:
			f.write("".join(recv.split("\r\n\r\n")[1:]))
		sock.close()



""" GET contents from a URL in multiple threads. 
Accepts URL as command line argument. 
"""
def get(url):
	url = urlparse(url)
	HOSTNAME = url.hostname
	PORT = url.port or 80
	PATH = url.path
	logging.info("[Host: %s Port: %s Path: %s]", HOSTNAME, PORT, PATH)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((HOSTNAME, PORT))
	except socket.error, msg:
		sys.stderr.write("[ERROR] %s\n" % msg[1])
		sys.exit(1)
	# Send HEAD Request to fetch Headers 
	sock.send("HEAD %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (PATH, HOSTNAME))
	data = sock.recv(1024)
	recv = ""
	while len(data):
		recv = recv + data
		data = sock.recv(1024)
	sock.close()
	# Parse Headers using MIMETools to Fetch Content-Length
	request_line, headers_alone = recv.split('\r\n', 1)
	headers = Message(StringIO(headers_alone))
	content_length = headers['content-length']
	logging.info("[Content-Length: %s]",content_length)
	# initialize threads for download
	thread_count = THREAD_COUNT;
	bytes_per_thread = int(content_length)/thread_count;
	clients = []
	for x in xrange(0,thread_count):
		start_range = (x)*bytes_per_thread
		if x is not 0:
			start_range += 1
		end_range = (x+1)*bytes_per_thread
		if x == (thread_count-1):
			end_range = int(content_length) - 1
		client = Client(x,HOSTNAME,PORT,PATH,start_range,end_range)
		clients.append(client)
	for x in xrange(0,thread_count):
		clients[x].start()
	while threading.active_count() > 1:
		time.sleep(1)
		logging.info("Download Thread Running")
	logging.info("Joining Files")
	# Joining partfiles using cat
	file_name = os.path.basename(PATH)
	os.system("cat partfile? > "+os.path.basename(file_name))
	# Removing Partfiles
	os.system("rm partfile?")
	logging.info("Exiting")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# Initializing Argparse with 2 options URL and --log
	parser.add_argument("url", help="Enter the URL to Fetch Content")
	parser.add_argument("--log", type=str,
                    help="Set Log Level(DEBUG INFO WARNING CRITICAL)")
	args = parser.parse_args()
	# Fetching and initializing Log Level
	if args.log is not None:
		level = LEVELS.get(args.log, logging.NOTSET)
		logging.basicConfig(level=level)
	# Initialize GET Request
	get(args.url)