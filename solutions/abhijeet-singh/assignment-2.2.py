import urllib2
from HTMLParser import HTMLParser
import threading

class MyHTMLParser(HTMLParser):
	lock = threading.Lock()ss
	def handle_starttag(self, tag, attrs):
		if tag == "link" or tag == "img"  or tag == "script":
			for attr in attrs:
				if attr[0] == "href" or attr[0] == "src":
					self.lock.acquire()
					print url+attr[1]+" Download Started"
					self.lock.release()
					thread = threading.Thread(target = self.download, args=(url, attr[1]))
					thread.start()
				

	def download(self, url, attribute):
		response = urllib2.urlopen(url+attribute)
		webcontent = response.read()
		g=open(attribute, "w")
		g.write(webcontent)
		g.close()
		self.lock.acquire()
		print url+attribute+" Download Finished"
		self.lock.release()
	
def main(url):
	response = urllib2.urlopen(url)
	webContent = response.read()
	g = open("index.html", "w")
	g.write(webContent)
	g.close()
	parser = MyHTMLParser()
	parser.feed(webContent)

if __name__ == '__main__':
	url = raw_input("Enter a url ")
	main(url)
