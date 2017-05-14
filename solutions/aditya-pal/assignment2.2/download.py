import threading
import socket
import tempfile
import logging
import sys
import os


def get_headers(path, host, req_type, start_byte, end_byte):
    header = ""
    dict = {}
    dict["endline"] = "\r\n"
    dict["request"] = "%s %s HTTP/1.1" % (req_type, path)
    dict["host"] = "Host: %s" % (host)
    dict["range"] = "Range: bytes=%s-%s" % (str(start_byte), str(end_byte))
    if (start_byte == 0 and end_byte == 0):
        dict["range"] = ""
    header += dict["request"]
    header += dict["endline"]
    header += dict["host"]
    header += dict["endline"]
    header += dict["range"]
    header += dict["endline"]
    header += dict["endline"]
    return header


class Download_File_Thread(threading.Thread):
    def __init__(self, host, path, port, start, end, thread_num, files):
        threading.Thread.__init__(self)
        self.host = host
        self.path = path
        self.port = port
        self.start_byte = start
        self.end_byte = end
        self.thread_num = thread_num
        self.files = files

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
        except socket.error:
            logging.info("Could Not Establish Connection, Download Failed")
            raise Exception("Error : Could Not Connect To Download Link")
        headers = get_headers(
            self.path,
            self.host,
            "GET",
            self.start_byte,
            self.end_byte
        )
        client_socket.send(headers)
        received_data = ""
        while True:
            file_data = client_socket.recv(1024)
            if not file_data:
                break
            received_data += file_data
        file = tempfile.NamedTemporaryFile(delete=False)
        self.files.append(file.name)
        file.write(received_data)
        file.close()


class Download_Manager():
    def __init__(self, host, path, port, thread_count):
        self.host = host
        self.path = path
        self.port = port
        self.thread_count = thread_count
        self.threads = []
        self.files = []

    def download(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
        except socket.error:
            logging.info("Could Not Establish Connection, Download Failed")
            raise Exception("Error : Could Not Connect To Download Link")
        header_request = get_headers(self.path, self.host, "HEAD", 0, 0)
        client_socket.send(header_request)
        response_data = ""
        while True:
            response = client_socket.recv(1024)
            if not response:
                break
            response_data += response
        header_data = response_data
        header_len = len(header_data)
        first_index = response_data.find("Content-Length")
        response_data = response_data[first_index + 16:]
        last_index = response_data.find("\r\n")
        response_data = response_data[: last_index]
        response_data.strip()
        content_length = 0
        try:
            content_length = int(response_data)
            if content_length <= 0:
                logging.info("No Meta Data")
                raise Exception("Error : No Meta Data")
        except ValueError:
            logging.info("Incorrect Meta Data")
            raise Exception("Error : Incorrect Meta Data")
        chunk_size = (content_length / self.thread_count)
        start_byte = 0
        thread_num = 0
        logging.info("Download Starting ...")
        while start_byte < content_length:
            end_byte = min(start_byte + chunk_size, content_length - 1)
            thread = Download_File_Thread(
                self.host,
                self.path,
                self.port,
                start_byte,
                end_byte,
                thread_num,
                self.files
            )
            start_byte = end_byte + 1
            thread_num += 1
            self.threads.append(thread)
            thread.start()
        logging.info("Joining Threads ...")
        for thread in self.threads:
            thread.join()
        outfile = os.path.basename(os.path.basename(self.path))
        output_file = open(outfile, 'w')
        logging.info("Writing To File ...")
        data = ""
        for num in range(thread_num):
            file = open(self.files[num])
            file.seek(0)
            for line in file:
                data += line
            file.close()
            os.unlink(self.files[num])
        x = (header_data[-8:])
        p = data.rfind(x, header_len + 1)
        output_file.write(data[p + 8:])
        logging.info("Download Completed Successfully !!!")


def inputs(hostname, path, port, thread_count):
    logging.basicConfig(level=logging.INFO)
    download_file = Download_Manager(hostname, path, port, thread_count)
    download_file.download()
