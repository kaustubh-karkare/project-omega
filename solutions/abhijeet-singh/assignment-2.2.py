import os
import urllib2
import socket
import threading

class downloader() :
	threads = []
	saveFile = None
	#init the class and divide the download for the thread
	def __init__(self, url, part, size, name) :
		self.url = url
		self.part = int(part)
		self.size = int(size)
		self.partSize = self.size/self.part
		self.name = name
		self.saveFile = open(self.name, "w")
		print "Downloading..."
		for i in range(0, self.part) :
			t = threading.Thread(target=self.download, args = (i*self.partSize, i+1*self.partSize, i))
			t.start()
			self.threads.append(t)
		if (self.size - self.part*self.partSize) != 0 :
			t = threading.Thread(target=self.download, args = (self.part*self.partSize, self.size, self.part))
			t.start()
			self.threads.append(t)
	
	#for each thread download the part for the thread and write it to the file
	def download(self, start, end, index) :
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)', 'Connection': 'Keep-Alive', 
'Range': 'bytes='+str(start)+'-'+str(end)}
		req = urllib2.Request(self.url, headers=headers)
		try :
			r = urllib2.urlopen(req)
			self.saveFile.seek(start)
			self.saveFile.write(r.read())			
		except socket.error :
			print "Error in Connection"

	#ensures that all the thread are finished
	def finish(self) :
		for i in self.threads:
			i.join()
		self.saveFile.close()

#checks whether the given url is correct or not and then tells downloader to download it
def URLcheck(url, part) :
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)', 'Connection': 'Keep-Alive'}
	req = urllib2.Request(url, headers=headers)
	try :
		r = urllib2.urlopen(req)
		print "File Name " + os.path.basename(url)
		print "File Size " + str(int(r.info().getheaders("Content-Length")[0])/1024/1024)+" MB"
		print "Download Starting..."
		d = downloader(url, part, r.info().getheaders("Content-Length")[0],  os.path.basename(url))
		d.finish()
		print "Download Finished!!!"
	except urllib2.URLError, e :
		print "Wrong Url"
	except socket.error :
		print "Error in Connection"
	
#takes input from user about what to download
if __name__ == '__main__':
	url = raw_input("Enter URL To Download ")
	while True :
		try:
			part = raw_input("Enter number of parts you think should be required to download the file ")
        		value = int(part)
			break
		except ValueError:
			print "Error: Enter a positive number. "
	URLcheck(url, part)
