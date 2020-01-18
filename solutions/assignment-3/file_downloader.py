import socket
import os
import re

class Downloader():

    def __init__(self, url, save_as):
        self.host, self.port, self.resource = self._find_server_and_resouce(url)
        if not self.port:
            self.port = 80
        else:
            self.port = int(self.port)
        if not self.resource:
            self.resource = '/'
        self.url = url
        self.save_as = save_as

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self._send()
        self._receive()

    def stop(self):
        self.sock.close()

    def _send(self):
        request = self._generate_request(self.resource, self.host)
        self.sock.sendall(request)

    def _receive(self):
        header_data = self._get_response_headers()
        print(header_data)
        content_length = self._get_content_length(header_data)
        print(content_length)
        self._download_payload(content_length)

    def _get_response_headers(self):
        response_msg = ''
        msg_buffer = self.sock.recv(1)
        response_msg += msg_buffer.decode()
        #print(response_msg)
        while response_msg[-4:] != '\r\n\r\n':
            msg_buffer = self.sock.recv(1)
            response_msg += msg_buffer.decode()
        return response_msg

    def _get_content_length(self, header_data):
        seek = header_data.find('Content-Length') + 16
        content_length = ''
        while header_data[seek] != '\r':
            content_length += header_data[seek]
            seek += 1
        return int(content_length)

    def _download_payload(self, content_length):
        download_length = 0
        with open(self.save_as, 'wb') as download_file:
            while download_length < content_length:
                packet = self.sock.recv(content_length - download_length)
                if not packet:
                    return None
                download_length += len(packet)
                download_file.write(packet)

    def _generate_request(self, resource, server_addr):
        GET_request = ("GET %s HTTP/1.1\r\n"
                       "Host: %s\r\n"
                       "Accept: */*\r\n\r\n" % (resource, server_addr)).encode()
        return GET_request


    @staticmethod
    def _find_server_and_resouce(url):
        regex_pattern = '^(?:http://)([^:\/?]+)(?:[\:]?)([0-9]*)(?:\/?)([\S]*)$'
        pattern_obj = re.compile(regex_pattern)
        assert (url.partition('://')[0] == 'http'), "Error! Script can only work for HTTP based servers."
        host, port, resource = pattern_obj.findall(url)[0]
        return host, port, resource
