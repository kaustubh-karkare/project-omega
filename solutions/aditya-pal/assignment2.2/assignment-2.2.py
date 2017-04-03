import argparse
import urlparse
import threading
import socket
import tempfile
import logging
import sys
import os
   

def request(path, host, req_type, start_byte, end_byte):
    if (start_byte == 0 and end_byte == 0):
        byte_range = ""
    else:
        byte_range = "Range: bytes=%s-%s\r\n" %(str(start_byte), str(end_byte))
    header = "%s %s HTTP/1.1\r\nHost: %s\r\n" %(req_type, path, host)
    header += (byte_range + "\r\n")
    return header
    
    

class Download_File_Thread(threading.Thread):
    def __init__(self, host, path, port, start_byte, end_byte, thread_num):
        threading.Thread.__init__(self)
        self.host = host
        self.path = path
        self.port = port
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.thread_num = thread_num
        
    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
        except socket.error:
            logging.info("Could Not Establish Connection, Download Failed")
            sys.exit(0)
        data_request = request(
                                        self.path,
                                        self.host,
                                        "GET",
                                        self.start_byte,
                                        self.end_byte
                                )
        client_socket.send(data_request)
        received_data = ""
        while (True):
            file_data = client_socket.recv(1024)
            if not file_data:
                break
            received_data += file_data
        filename = 'tempfile'+str(self.thread_num)
        file = open(filename, 'w')
        file.write(received_data)
        
class Download_Manager():
    def __init__(self, host, path, port, thread_count):
        self.host = host
        self.path = path
        self.port = port
        self.thread_count = thread_count
        self.threads = []

    def download(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
        except socket.error:
            logging.info("Could Not Establish Connection, Download Failed")
            sys.exit(0)
        header_request = request(self.path, self.host, "HEAD", 0, 0)
        client_socket.send(header_request)
        response_data = ""
        while (True):
            response = client_socket.recv(1024)
            if not response:
                break
            response_data += response
        header_data = response_data
        print (header_data)
        first_index = response_data.find("Content-Length")
        response_data = response_data[first_index + 16 : ]
        last_index = response_data.find("\r\n")
        response_data = response_data[ : last_index]
        response_data.strip()
        content_length = 0
        try:
            content_length = int(response_data)
            if (content_length <= 0):
                logging.info("No Meta Data, Exiting ...")
                sys.exit(0)
        except ValueError:
            logging.info("Incorrect Meta Data, Exiting ...")
            sys.exit(0)
        chunk_size = (content_length / thread_count)
        start_byte = 0
        thread_num = 0
        logging.info("Download Starting ...")
        while (start_byte < content_length):
            end_byte = min(start_byte + chunk_size, content_length - 1)
            thread = Download_File_Thread(
                                            self.host,
                                            self.path,
                                            self.port,
                                            start_byte,
                                            end_byte,
                                            thread_num
                                    )
            start_byte = end_byte + 1
            thread_num+=1
            self.threads.append(thread)
        for thread in self.threads:
            thread.start()
        logging.info("Joining Threads ...")
        for thread in self.threads:
            thread.join()
        outfile = os.path.basename(os.path.basename(self.path))
        output_file = open(outfile, 'w')
        logging.info("Writing To File ...")
        s = ""
        for num in range(thread_num):
            filename = 'tempfile'+str(num)
            temp_file = open(filename, 'r')
            for line in temp_file:
                s += line
            os.remove(filename)
        x = (header_data[-8:])
        p = s.find(x)
        output_file.write(s[p+8:])
        logging.info("Download Completed Successfully !!!")

            
if __name__ == '__main__' :
    arguments = argparse.ArgumentParser()
    arguments.add_argument(
            "-u",
            "--url",
            required = True,
            help = "URL of File to be Downloaded"
        )
    arguments.add_argument(
            "-t",
            "--threads",
            default = 3,
            required = False,
            help = "Number of Threads in which File will be downloaded"
        )
    arguments.add_argument(
            "-p",
            "--port",
            default = 80,
            required = False,
            help = "Port Number for file download"
        )
    args = arguments.parse_args()
    url_elements = urlparse.urlparse(args.url)
    thread_count = int(args.threads)
    port = int(args.port)
    logging.basicConfig(level=logging.INFO)
    download_file = Download_Manager(url_elements.hostname, url_elements.path, port, thread_count)
    download_file.download()
