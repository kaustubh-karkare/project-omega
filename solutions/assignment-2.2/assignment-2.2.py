import socket
import threading
import math
import tempfile
import argparse
import logging
import collections
import re
import responseheaders

BUFF_SIZE = 1024


def download(client_socket, request_message, download_file):
    client_socket.send(request_message)
    while True:
        data = client_socket.recv(BUFF_SIZE)
        if not data:
            break
        try:
            headers, data = data.split('\r\n\r\n')
            download_file.write(data)
        except:
            download_file.write(data)
    download_file.flush()
    client_socket.close()


def connect_client(host, port):
    port = int(port)
    client_socket = socket.socket()
    try:
        client_socket.connect((host, port))
    except:
        logging.error('Client socket connection could not be established')
        raise
    return client_socket


def temporary_file():
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        return(temp_file)
    except:
        logging.error('Temporary file could not be created')
        raise


class DownloadFile(threading.Thread):

    def __init__(self, url, threads, output_path):
        self.url = url
        self.threads = threads
        self.output_path = output_path
        threading.Thread.__init__(self)

    def run(self):
        self.parse_url()
        self.response_headers()
        self.download_files()
        self.merge_downloaded_files()

    def parse_url(self):
        self.pattern = (r'(https?)?(\:\/\/)?([a-zA-Z0-9-.]+)?\:?(\d+)?(.*)')
        self.url_group = re.match(self.pattern, self.url)
        self.UrlParser = collections.namedtuple('UrlParser', 'host port path')
        self.parsed_url = (
            self.UrlParser(
                self.url_group.group(3),
                self.url_group.group(4),
                self.url_group.group(5)
            )
        )

    def response_headers(self):
        self.client_socket = (
            connect_client(
                self.parsed_url.host,
                self.parsed_url.port
            )
        )
        self.headers = (
            responseheaders.get_headers(
                self.client_socket,
                self.parsed_url
            )
        )
        self.client_socket.close()

    def download_files(self):
        if (self.headers['Accept-Ranges'] != 'bytes'):
            self.threads = 1
        self.each_file_bytes = int(
            math.ceil(
                int(self.headers['Content-Length']) /
                self.threads
            )
        )
        self.download_request_message = (
            'GET ' +
            self.parsed_url.path +
            ' HTTP/1.1\r\n' +
            'Host: ' +
            self.parsed_url.host +
            '\r\n' +
            'Connection: close\r\n' +
            'Range: bytes='
        )
        self.start_range = 0
        self.end_range = self.each_file_bytes
        self.downloaded_file_names = []
        self.download_threads = []
        while self.threads > 0:
            if (self.start_range > int(self.headers['Content-Length']) - 1):
                # File already downloaded
                break
            if (self.end_range > int(self.headers['Content-Length']) - 1):
                self.end_range = int(self.headers['Content-Length']) - 1
            self.download_file = temporary_file()
            self.downloaded_file_names.append(self.download_file.name)
            self.client_socket = (
                connect_client(
                    self.parsed_url.host,
                    self.parsed_url.port
                )
            )
            self.download_threads.append(
                threading.Thread(
                    target=download,
                    args=(
                        self.client_socket,
                        self.download_request_message +
                        str(self.start_range) +
                        '-' +
                        str(self.end_range) +
                        '\r\n\r\n',
                        self.download_file
                    )
                )
            )
            self.download_threads[len(self.download_threads) - 1].start()
            self.start_range = self.end_range + 1
            self.end_range = self.start_range + self.each_file_bytes
            self.threads -= 1

        self.i = 0
        while self.i < len(self.download_threads):
            self.download_threads[self.i].join()
            self.i += 1

    def merge_downloaded_files(self):
        try:
            self.output_file = open(self.output_path, 'w')
        except:
            logging.error('Output file could not be created')
            raise
        self.i = 0
        while self.i < len(self.download_threads):
            self.downloaded_file_name = (
                self.downloaded_file_names[self.i]
            )
            self.downloaded_file = open(self.downloaded_file_name, 'r')
            self.downloaded_file.seek(0)
            self.output_file.write(self.downloaded_file.read())
            self.downloaded_file.close()
            self.i += 1


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
        '-o',
        type=str,
        required=True,
        help='Downloaded file name'
    )
    parsed_argument = parser.parse_args()
    DownloadFile(
        url=parsed_argument.url,
        threads=parsed_argument.threads,
        output_path=parsed_argument.output_path
    ).start()

if __name__ == '__main__':
    main()
