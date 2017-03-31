import os
import socket
import threading
import logging
import argparse
import tempfile

class DownloadManager():
	
	def __init__(self, url, port , parts):
		self.threads = []
		self.file_parts = []
		self.logger = logging.getLogger("Download manager")
		logging.basicConfig(level=logging.INFO)
		self.url = url
		self.parts = int(parts)
		self.logger.info("Download initied")
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		host_index = self.url.find('/')
		self.host = self.url[: host_index]
		self.path = self.url[host_index :]
		ip = socket.gethostbyname(self.host)
		port = int(port)
		self.client.connect((ip,port))
		header = self.get_http_header(0, 0)
		try:
			self.client.send(header)
			self.client_received = self.client.recv(1024)
		except socket.error:
			self.logger.warn("Download failed")
	
	# download starts over here
	def start(self):
		self.save_file = open(os.path.basename(self.url), "w")
		self.logger.info("Downloading File --> {}".format(os.path.basename(
			self.url)))
		# for finding content-length from header
		start_content_length = self.client_received.lower() \
			.find('content-length: ')
		end_content_length = self.client_received.find('\r\n', 
			start_content_length + 16)
		file_size = int(self.client_received[start_content_length+16 : 
			end_content_length])
		start = 0		
		for thread_num in range(0, self.parts + 1):	
			temp_file = tempfile.TemporaryFile()
			self.file_parts.append(temp_file)
			thread = threading.Thread(target=self.thread_download, args = (start
				, file_size / self.parts*thread_num, temp_file))
			start = (file_size/self.parts) * thread_num + 1
			if thread_num == self.parts:
				thread = threading.Thread(target=self.thread_download, args = (
					start, file_size, temp_file))
			thread.start()
			self.threads.append(thread)
			
	# waiting for all the threads to end and end the download process
	def wait(self):
		for thread in self.threads:
			thread.join()
		for file_part in self.file_parts:
			file_part.seek(0)
			data = file_part.read()
			self.save_file.write(data)
			file_part.close()
		self.save_file.close()
		self.client.close()
		self.logger.info("Download Finished")
	
	# for each thread download the parts for the thread and write it to the file
	def thread_download(self, start, end, temp_file):
		header = self.get_http_header(start, end)
		self.client.send(header)
		while True:
			data = self.client.recv(1024)
			if not data:
  				break
			temp_file.write(data)

	# returns the http header request
	def get_http_header(self, start, end):
		if start == 0 and end == 0:
			byte_range = ""
		else: 
			byte_range = 'bytes='+str(start)+'-'+str(end)		
		header = 'GET ' + self.path + ' HTTP/1.1\r\nHost: ' + \
			self.host
		header += '\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, ' + \
			'deflate\r\nAccept: */*'
		header += '\r\nUser-Agent: python-requests/2.13.0\r\nRange: ' \
			+ byte_range + '\r\n\r\n'
		return header

	
# takes input from user about what to download
if __name__ == '__main__':
	download_info = argparse.ArgumentParser()
	download_info.add_argument("-u", "--url", help = "Url from where file \
		will be downloaded", required = True)
	download_info.add_argument("-p", "--port", help = "Port on which file \
		will be downloaded", default = '80')
	download_info.add_argument("-pa", "--parts", help = "Parts in which file \
		will be downloaded", default = '3')
	url = download_info.parse_args().url
	if url[:7] == 'http://':
		url = url[7:]
	download =	DownloadManager(url, download_info.parse_args().port,
		download_info.parse_args().parts)
	download.start()
	download.wait()	

