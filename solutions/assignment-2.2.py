import socket
import threading
import math
import tempfile
import argparse
import logging

BUFF_SIZE = 1024


class DownloadRange(threading.Thread):

    def __init__(
        self,
        host,
        port,
        path,
        start_position,
        end_position,
        range_download_file,
        header_count
    ):
        self.host = host
        self.port = port
        self.path = path
        self.start_position = start_position
        self.end_position = end_position
        self.range_download_file = range_download_file
        self.header_count = header_count
        self.range_to_get = str(self.start_position) + '-'
        self.range_to_get += str(self.end_position)
        self.request = 'GET ' + self.path + 'HTTP/1.1\n'
        self.request += 'Host: ' + self.host + '\n'
        self.request += 'Range: bytes=' + self.range_to_get + '\n\n'
        threading.Thread.__init__(self)

    def run(self):
        self.download_range()

    def download_range(self):
        self.client_socket = socket.socket()
        try:
            self.client_socket.connect((self.host, self.port))
        except:
            logging.error('Could not establish connection')
        self.client_socket.send(self.request)
        self.receiving_data_file = tempfile.NamedTemporaryFile()
        self.receiving_data_file_name = self.receiving_data_file.name
        while True:
            self.data_received = self.client_socket.recv(BUFF_SIZE)
            if not self.data_received:
                break
            self.receiving_data_file.write(self.data_received)
        self.receiving_data_file.flush()
        try:
            self.temp_downloaded_file = open(
                self.receiving_data_file_name, 'r'
            )
        except:
            logging.error('File connection could not be established')
        self.i = 0
        while self.i <= self.header_count:
            self.temp_downloaded_file.readline()
            self.i += 1
        self.range_download_file.write(self.temp_downloaded_file.read())
        self.range_download_file.flush()


class DownloadFile(threading.Thread):

    def __init__(self, host, port, path, threads, output_file):
        self.host = host
        self.port = port
        self.path = path
        self.threads = threads
        self.output_file = output_file
        self.request = self.path + 'HTTP/1.1\n'
        self.request += 'Host: ' + self.host + '\n'
        self.request += 'Range: bytes=0-' + '\n\n'
        threading.Thread.__init__(self)

    def run(self):
        self.get_response_headers()
        self.download_file()

    def get_response_headers(self):
        self.client_socket = socket.socket()
        try:
            self.client_socket.connect((self.host, self.port))
        except:
            logging.error('Could not establish connection')
        self.client_socket.send('HEAD ' + self.request)
        self.received_headers = ''
        while True:
            self.data_received = self.client_socket.recv(BUFF_SIZE)
            if not self.data_received:
                break
            self.received_headers += self.data_received
        self.received_headers = (self.received_headers).splitlines()
        self.headers = {}
        self.i = 1
        while (
            self.i < len(self.received_headers) and
            self.received_headers[self.i]
        ):
            self.curr_header = self.received_headers[self.i]
            self.split_headers = (self.curr_header).split(':')
            self.headers[self.split_headers[0]] = self.split_headers[1]
            self.i = self.i + 1

    def download_file(self):
        self.content_length = int(self.headers['Content-Length'])
        self.start_position = 0
        self.end_position = self.content_length - 1
        self.accept_range_allowed = False
        if (self.headers['Accept-Ranges'] == ' bytes'):
            self.accept_range_allowed = True

        if (self.accept_range_allowed is False):
            self.range_download_file = tempfile.NamedTemporaryFile()
            self.range_download_file_name = self.range_download_file.name
            self.thread1 = DownloadRange(
                self.host,
                self.port,
                self.path,
                self.start_position,
                self.end_position,
                self.temp_file,
                len(self.headers) + 1
            )
            self.thread1.start()
            self.thread1.join()
            self.downloaded_range = open(self.range_download_file_name, 'r')
            self.output_file.write(self.download_range.read())

        else:
            self.each_file_bytes = int(
                math.ceil(
                    self.content_length /
                    self.threads
                )
            )
            self.start_range = 0
            self.end_range = self.each_file_bytes
            self.range_download_file_names = []
            self.thread_instances = []
            while self.threads > 0:
                if (self.start_range > self.end_position):
                    break
                if (self.end_range > self.end_position):
                    self.end_range = self.end_position
                try:
                    self.range_download_file = tempfile.NamedTemporaryFile()
                except:
                    logging.error('File connection could not be established')
                self.range_download_file_names.append(
                    self.range_download_file.name
                )
                self.thread_instances.append(
                    DownloadRange(
                        self.host,
                        self.port,
                        self.path,
                        self.start_range,
                        self.end_range,
                        self.range_download_file,
                        len(self.headers) + 1
                    )
                )
                self.thread_instances[len(self.thread_instances) - 1].start()
                self.start_range = int(self.end_range) + 1
                self.end_range = (
                    int(self.start_range) +
                    int(self.each_file_bytes)
                )
                self.threads -= 1
            self.i = 0
            while self.i < len(self.thread_instances):
                self.thread_instances[self.i].join()
                self.i += 1
            self.i = 0
            while self.i < len(self.thread_instances):
                self.downloaded_file_name = (
                    self.range_download_file_names[self.i]
                )
                self.downloaded_range = open(self.downloaded_file_name, 'r')
                self.downloaded_range.seek(0)
                self.output_file.write(self.downloaded_range.read())
                self.downloaded_range.close()
                self.i += 1


class UrlParser:

    def __init__(self, url):
        self.url = url
        self.protocol_of_url = self.protocol()

    def protocol(self):
        if (self.url.find('://') != -1):
            self.split_url = self.url.split('://')
            self.url = self.split_url[1]
            return self.split_url[0]
        else:
            return ''

    def host(self):
        self.i = 0
        while (
            self.i < len(self.url) and
            self.url[self.i] != ':' and
            self.url[self.i] != '/'
        ):
            self.i += 1
        self.host_name = self.url[:self.i]
        self.url = self.url[self.i:]
        return self.host_name

    def port(self):
        if (self.url != '' and self.url[0] == ':'):
            self.port_number = self.url[1:self.url.find('/')]
            self.url = self.url[self.url.find('/'):]
            if (self.port_number == '8080'):
                self.port_number = '80'
            return int(self.port_number)
        else:
            if (self.protocol_of_url == 'HTTPS'):
                return 80
            else:
                # Assuming protocol to be HTTPS
                return 80

    def path(self):
        return self.url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL to download'
    )
    parser.add_argument(
        '--threads',
        type=int,
        required=False,
        default=4,
        help='Number of threads to download'
    )
    parser.add_argument(
        '--output-path',
        '-op',
        type=str,
        required=True,
        help='Downloaded file name'
    )
    parsed_argument = parser.parse_args()
    url_parser = UrlParser(parsed_argument.url)
    host = url_parser.host()
    port = url_parser.port()
    path = url_parser.path() + ' '
    threads = parsed_argument.threads
    output_path = parsed_argument.output_path
    try:
        output_file = open(output_path, 'w')
    except:
        logging.error('Output file could not be established')
    DownloadFile(
        host,
        port,
        path,
        threads,
        output_file
    ).start()

if __name__ == '__main__':
    main()
