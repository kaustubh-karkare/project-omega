import socket
import sys
import logging
import argparse
import threading
import time
from mimetools import Message
from StringIO import StringIO
import os
import re
LEVELS = {'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}
THREAD_COUNT = 4

class SocketConnection():
	def __init__(self, hostname, port):
		self.hostname = hostname
		self.port = port

	def __enter__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.connect((self.hostname, self.port))
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)
		return self.sock

	def __exit__(self, exc_type, exc_value, traceback):
		if exc_type is not None:
			print exc_type, exc_value, traceback
		self.sock.close()
		return self


class DownloadThread (threading.Thread):
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
		# Establish Socket Connection
		with SocketConnection(self.hostname, self.port) as sock:
			# Send HEAD Request to fetch Headers  
			sock.send("GET %s HTTP/1.1\r\nHost: %s\r\nRange: bytes=%s-%s\r\nConnection: close\r\n\r\n"
				% (self.path, self.hostname, self.start_range, self.end_range))
			data = sock.recv(512)
			recv = ""
			while len(data):
				recv = recv + data
				data = sock.recv(512)
		# Write to Partfile after removing Headers
		with open('partfile' + str(self.thread_id),'w') as f:
			f.write("".join(recv.split("\r\n\r\n")[1:]))


def parse_url(url):
	url_pattern = re.compile("(https?)?(\:\/\/)?([a-zA-Z0-9.]+)\:?(\d+)?(.*)")
	url_group = url_pattern.match(url)
	return url_group

""" GET contents from a URL in multiple threads. 
Accepts URL as command line argument. 
"""
def get(url):
	url = parse_url(url)
	hostname = url.group(3)
	port = url.group(4) or 80
	path = url.group(5)
	logging.info("[Host: %s port: %s path: %s]", hostname, port, path)
	# Establish Socket Connection
	with SocketConnection(hostname, port) as sock:
		# Send HEAD Request to fetch Headers 
		sock.send("HEAD %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, hostname))
		data = sock.recv(1024)
		recv = ""
		while len(data):
			recv = recv + data
			data = sock.recv(1024)
	# Parse Headers using MIMETools to Fetch Content-Length
	request_line, headers_alone = recv.split('\r\n', 1)
	headers = Message(StringIO(headers_alone))
	content_length = headers['content-length']
	logging.info("[Content-Length: %s]",content_length)
	# initialize threads for download
	thread_count = THREAD_COUNT;
	bytes_per_thread = int(content_length)/thread_count;
	download_threads = []
	for x in xrange(0,thread_count):
		start_range = (x) * bytes_per_thread
		if x is not 0:
			start_range += 1
		end_range = (x+1) * bytes_per_thread
		if x == (thread_count-1):
			end_range = int(content_length) - 1
		download_thread = DownloadThread(x,hostname,port,path,start_range,end_range)
		download_threads.append(download_thread)
	for x in xrange(0,thread_count):
		download_threads[x].start()
	while threading.active_count() > 1:
		time.sleep(1)
		logging.info("Download Thread Running")
	logging.info("Joining Files")
	# Joining partfiles
	file_name = os.path.basename(os.path.basename(path))
	with open(file_name, 'w') as outfile:
	    for x in xrange(0,thread_count):
	        with open("partfile" + str(x)) as infile:
	            for line in infile:
	                outfile.write(line)
	# Removing Partfiles
	for x in xrange(0,thread_count):
		os.remove("partfile" + str(x))
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
