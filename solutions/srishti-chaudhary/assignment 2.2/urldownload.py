#!/usr/bin/python

import sys, urlparse
import socket, string
import os

CRLF = "\r\n"

class SimpleClient:
    "Client support class for simple Internet protocols."

    def __init__(self, host, port):
        "Connect to an Internet server."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.file = self.sock.makefile("rb") # buffered

    def writeline(self, line):
        "Send a line to the server."
        self.sock.send(line + CRLF) # unbuffered write

    def download(self, document):
        "Read data from server and download into current directory."
		file_name = document.split('/')[-1]
		downloaded_file = os.path.join('C:/projectOmega', file_name)
		data = self.file.read()
		with open(downloaded_file, "wb") as code:
			code.write(data)
        
		return downloaded_file

    def readline(self):
        "Read a line from the server.  Strip trailing CR and/or LF."
        s = self.file.readline()
        if not s:
            raise EOFError
        if s[-2:] == CRLF:
            s = s[:-2]
        elif s[-1:] in CRLF:
            s = s[:-1]
        return s

class HTTPClient(SimpleClient.SimpleClient):
    """An HTTP client protocol support class"""

    def __init__(self, host):

        # extract port from hostname, if given
        try:
            i = string.index(host, ":")
            host, port = host[:i], string.atoi(host[i+1:])
        except ValueError: # catches both index and atoi errors
            port = 80

        SimpleClient.SimpleClient.__init__(self, host, port)

    def httpcmd(self, command, document):srishti
        "Send command, and return status code and list of headers."

        self.writeline("%s %s HTTP/1.0" % (command, document or "/"))
        self.writeline("")

        self.sock.shutdown(1) # close client end

        status = string.split(self.readline())

        if status[0] != "HTTP/1.0":
            raise IOError, "unknown status response"

        try:
            status = string.atoi(status[1])
        except ValueError:
            raise IOError, "non-numeric status code"

        headers = []
        while 1:
            line = self.readline()
            if not line:
                break
            headers.append(line)

        return status, headers

    def get(self, document):
        "Get a document from the server. Return status code and headers."

        return self.httpcmd("GET", document)

    def head(self, document):
        "Get headers from the server. Return status code and headers."

        return self.httpcmd("HEAD", document)

    def getbody(self, document):
        "Get document body"

        return self.download(document)

def get(url):

    # parse the URL (ignore most parts of it)
    spam, host, document, spam, spam, spam = urlparse.urlparse(url)

    # get the document
    http = HTTPClient(host)

    status, headers = http.get(document)
    if status != 200:
        return IOError, "couldn't read document"

    return http.getbody(document)
