import os
import socket
import threading
import logging
import argparse
import tempfile

class DownloadManager():
	
	def __init__(self, ip, port, url, parts):
		self.threads = []
		self.file_parts = []
		self.logger = logging.getLogger("Download manager")
		logging.basicConfig(level=logging.INFO)
		if url[ : 7] == 'http://':
			url = url[7 : ]
		host_index = url.find('/')
		self.host = url[ : host_index]
		self.path = url[host_index : ]
		self.parts = int(parts)
		self.logger.info("Download initied")
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if(ip == '0.0.0.0'):
			ip_client = socket.gethostbyname(self.host)
		else:
			ip_client = ip
		port = int(port)
		self.client.connect((ip_client,port))
		header = self.get_http_header('HEAD', 0, 0)
		try:
			self.client.send(header)
			client_received = self.client.recv(1024)
			self.header_information = {
				'HTTP Version': client_received[ : 8], 
				'Status': client_received[9 : 12]
			}
			start = 0
			self.end_dictionary = client_received.find('\r\n\r\n')
			while True:
				start = client_received.find('\r\n', start)
				tag_start = client_received.find(': ', start)
				tag_name = client_received[start + 2 : tag_start]
				end = client_received.find('\r\n', tag_start)
				start = end
				self.header_information[tag_name] = client_received[
					tag_start + 2 : end
				]
				if(start == self.end_dictionary):
					break
			#for i in self.header_information:
			#	print i+" : ", self.header_information[i]
		except socket.error:
			self.logger.warn("Download failed")
	
	# download starts over here
	def start(self):
		self.save_file = open(os.path.basename(self.path), "w")
		self.logger.info(
			"Downloading File --> {}".format(os.path.basename(self.path))
		)
		# for finding content-length from header information dictionary
		if self.header_information.has_key('Content-Length'):
			file_size = int(self.header_information['Content-Length'])
			start_byte = 0
			for thread_num in range(0, self.parts):	
				temp_file = tempfile.TemporaryFile()
				self.file_parts.append(temp_file)
				last_byte = (file_size / self.parts) * thread_num
				if thread_num == self.parts - 1:
					last_byte = file_size
				thread = threading.Thread(
					target=self.thread_download, 
					args=(start_byte, last_byte, temp_file)
				)
				start_byte = (file_size /  self.parts) * thread_num + 1
				thread.start()
				self.threads.append(thread)
		else:
			temp_file = tempfile.TemporaryFile()
			self.file_parts.append(temp_file)
			# -1, -1 because it has no Content-Length and therefore all 
			# information will be downloaded in a single tempfile & thread 
			thread = threading.Thread(
				target=self.thread_download, 
				args=(-1, -1, temp_file)
			)
			thread.start()
			self.threads.append(thread)
		
	# waiting for all the threads to end and end the download process
	def wait(self):
		for thread in self.threads:
			thread.join()
		for file_part in self.file_parts:
			if file_part == self.file_parts[0]:
				file_part.seek(self.end_dictionary + 4)
			else:
				file_part.seek(0)
			data = file_part.read()
			self.save_file.write(data)
			file_part.close()
		self.save_file.close()
		self.client.close()
		self.logger.info("Download Finished")
	
	# for each thread download the parts for the thread and write it to the file
	def thread_download(self, start_byte, last_byte, temp_file):
		header = self.get_http_header('GET', start_byte, last_byte)
		self.client.send(header)
		while True:
			data = self.client.recv(1024)
			if not data:
  				break
			temp_file.write(data)

	# returns the http header request
	def get_http_header(self, request, start_byte, last_byte):
		next_line = '\r\n'
		request_header = {
			'Connection': 'keep-alive',
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate',
			'User-Agent': 'python-requests/2.13.0'
		}
		header = request + ' ' + self.path + ' HTTP/1.1' + next_line
		header += 'Host: ' + self.host + next_line + 'Connection: '
		header += request_header['Connection'] + next_line
		header += 'Accept-Encoding: ' + request_header['Accept-Encoding']
		header += next_line + 'Accept: ' + request_header['Accept']
		header += next_line + 'User-Agent: ' + request_header['User-Agent']
		if start_byte == -1 and last_byte == -1:
			return_header = header + next_line + next_line
		else:
			if start_byte == 0 and last_byte == 0:
				byte_range = ""
			else:
				byte_range = 'bytes='+str(start_byte)+'-'+str(last_byte)
			header += next_line + 'Range: ' + byte_range
			return_header = header + next_line + next_line
		return return_header
	
# takes input from user about what to download
if __name__ == '__main__':
	download_info = argparse.ArgumentParser()
	download_info.add_argument(
		"-u", 
		"--url", 
		help="Url from where file will be downloaded", 
		required=True
	)
	download_info.add_argument(
		"-i",
		"--ip", 
		help ="IP on which file will be downloaded", 
		default='0.0.0.0'
	)
	download_info.add_argument(
		"-p",
		"--port", 
		help ="Port on which file will be downloaded", 
		default='80'
	)
	download_info.add_argument(
		"-t", 
		"--threads", 
		help="Number of threads in which file will be downloaded", 
		default='3'
	)
	download = DownloadManager(
		download_info.parse_args().ip,
		download_info.parse_args().port, 
		download_info.parse_args().url,
		download_info.parse_args().threads
	)
	download.start()
	download.wait()	

