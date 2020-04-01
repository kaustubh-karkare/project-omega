from parser import UrlParser
from header import RequestHeaderBuilder
from header import ResponseHeaderParser
from header import HEADER_END
from exception import InvalidUrl
import socket
import ssl

HTTPS = "https"
CHUNK_SIZE = 1024
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)


class UrlFileDownloader(object):
    """docstring for FileDownloader"""

    def __init__(self, url):
        super(UrlFileDownloader, self).__init__()
        self.url = UrlParser(url)
        self.download_filename = None

    def download(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if self.url.scheme == HTTPS:
                with context.wrap_socket(sock, server_hostname=self.url.host) as secure_sock:
                    secure_sock.connect((self.url.host, self.url.port))
                    self.send_request_header(secure_sock)
                    self.receive_response(secure_sock)
            else:
                sock.connect((self.url.host, self.url.port))
                self.send_request_header(sock)
                self.receive_response(sock)

    def send_request_header(self, sock):
        request_headers = RequestHeaderBuilder.create(
            method="GET",
            url_path=self.url.path_with_query,
            http_version="1.1",
            Host=self.url.host,
            Connection="close")
        sock.sendall(request_headers.encode())

    def receive_response(self, sock):
        header_data = b''
        body_data = b''
        while True:
            data = sock.recv(CHUNK_SIZE)
            if not data:
                break
            if HEADER_END.encode() in data:
                header_fragment, body_fragment = data.split(HEADER_END.encode(), 1)
                header_data += header_fragment
                body_data += body_fragment
                break
            header_data += data
        response_header = ResponseHeaderParser(header_data.decode(errors="ignore"))

        if response_header.response_code[0] != '2':
            raise InvalidUrl("url not reachable")

        filename = response_header.get_filename_from_response() or self.url.get_filename_from_url()
        if not filename or '.' not in filename:
            raise InvalidUrl("valid file/filename not found")
        self.download_file = filename
        with open(self.download_file, 'wb') as download_file:
            download_file.write(body_data)
            while True:
                data = sock.recv(CHUNK_SIZE)
                if not data:
                    break
                download_file.write(data)
