import os
import socket
import threading
from urlparse import urlparse
import logging

class DownloadManager():
	
	def __init__(self, url):
		self.lock = threading.Lock()
		self.threads = []
		self.logger = logging.getLogger("Download manager")
		logging.basicConfig(level=logging.INFO)
		self.url = url
		self.part = 3
		self.logger.info("Download initied ")
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.parsed_uri = urlparse(self.url)
		ip = socket.gethostbyname(self.parsed_uri.netloc)
		port = 80
		self.client.connect((ip,port))
		header = self.http_header(0, 0)
		try:
			self.client.send(header)
			client_received = self.client.recv(1024)
		except socket.error:
			self.logger.warn("Download failed ")			
		self.save_file = open(os.path.basename(self.url), "w")
		self.logger.info("Downloading File --> {}".format(os.path.basename(self.url)))
		# for finding content-length from header
		start_cl = client_received.lower().find('content-length: ')
		end_cl = client_received.find('\r\n', start_cl + 16)
		file_size = int(client_received[start_cl+16 : end_cl])
		start = 0
		for thread_num in range(0, self.part + 1):
			thread = threading.Thread(target=self.thread_download, args = (start, file_size / self.part*thread_num, thread_num))
			start = (file_size/self.part) * thread_num + 1
			if thread_num == self.part:
				thread = threading.Thread(target=self.thread_download, args = (start, file_size, thread_num))
			thread.start()
			self.threads.append(thread)
		for thread in self.threads:
			thread.join()
		self.save_file.close()
		self.client.close()
		self.logger.info("Download Finished ")
	
	# for each thread download the part for the thread and write it to the file
	def thread_download(self, start, end, index):
		header = self.http_header(start, end)
		self.client.send(header)		
		self.save_file.seek(start)
		while True:
			data = self.client.recv(1024)
			if not data:
  				break
			self.lock.acquire()
			self.save_file.write(data)
			self.lock.release()

	# returns the http header request
	def http_header(self, start, end):
		if start == 0 and end == 0:
			byte_range = ""
		else: 
			byte_range = 'bytes='+str(start)+'-'+str(end)		
		header = 'GET '+self.parsed_uri.path+' HTTP/1.1\r\nHost: '+self.parsed_uri.netloc
		header += '\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*'
		header += '\r\nUser-Agent: python-requests/2.13.0\r\nRange: '+byte_range+'\r\n\r\n'
		return header

	
# takes input from user about what to download
if __name__ == '__main__':
	url = raw_input("Enter URL To Download ")
	if url[:7] != 'http://':
		url = 'http://' + url
	DownloadManager(url)

