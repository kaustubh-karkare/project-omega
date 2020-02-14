import re
import datetime
import socket
from time import sleep

class HttpProtocol:

    CRLF = '\r\n'

    def __init__(self, sock):
        if sock:
            self.sock = sock
            self.sb = SocketBuffer(sock)

    def parse_headers(self, headers_data):
        headers = headers_data.strip().split(self.CRLF)
        parsed_headers = dict()
        unparsed_headers = list()
        for header_line in headers:
            try:
                header, data = header_line.split(': ', maxsplit=1)
                parsed_headers[header] = data
            except ValueError:
                unparsed_headers.append(header_line)
        return parsed_headers, unparsed_headers


    def download_payload(self, save_as, content_length):
        download_length = 0

        with open(save_as, 'wb') as download_file:
            while download_length < content_length:
                self.sb.recv()
                packet = self.sb.empty_buffer()
                if not packet:
                    return None
                download_length += len(packet)
                download_file.write(packet)

    def get_headers(self):
        '''
        Receive header data from socket
        '''
        response_msg = ''
        header_recv = False
        while not header_recv:
            self.sb.recv()
            while True:
                msg_buffer = self.sb.read_buffer(1).decode()
                if not msg_buffer:
                    break
                response_msg += msg_buffer
                if response_msg[-4:] == '\r\n\r\n':
                    header_recv = True
                    break
        return response_msg

    def send_data_chunks(self, chunk_size, file_handler, seek_start, seek_end):
        file_handler.seek(seek_start)
        while file_handler.tell() <= seek_end:
            data_chunk = file_handler.read(chunk_size)
            if not data_chunk:
                break
            self.sock.sendall(data_chunk)
            sleep(1)
        file_handler.close()

    @staticmethod
    def compute_request_ranges(content_length, parts):
        '''
        Calculates ranges to download the resource according to
        number of parts specified
        '''

        data_ranges = list()
        start = 0
        part_size = int((content_length) / parts)
        iters = parts - 1 if content_length % parts != 0 else parts

        for _ in range(iters):
            data_ranges.append(str(start) + "-" + str(start+part_size-1))
            start += part_size
        if start < content_length:
            data_ranges.append(str(start) + "-" + str(content_length-1))
        return data_ranges

    @staticmethod
    def find_server_and_resouce(url):
        '''
        Finds server, port and resorce path from url using regex

        regex_pattern -
            non-capturing group 1 : communication protocol
            capturing group 1: host
            non-capturing group 2: colon(:)
            capturing group 2: port number
            non-capturing group 3: slash(/) - unnecessary will rectify it later
            capturing group 3: path to resource
        '''
        regex_pattern = '^(?:\w+\:\/\/)?([^:\/?]+)(?:[\:]?)([0-9]*)(?:\/?)(.*)$'
        pattern_obj = re.compile(regex_pattern)
        assert (url.partition('://')[0] == 'http'), "Error! Script can only work for HTTP based servers."
        host, port, resource = pattern_obj.findall(url)[0]

        port = int(port) if port else 80 #assign default TCP port 80 if none assigned
        resource = '/' if not resource else resource

        return host, port, resource

class HttpRequest(HttpProtocol):

    def __init__(self, sock=None):
        super(HttpRequest, self).__init__(sock)

    def parse_request(self, request_data):
        parsed_headers, unparsed_headers = self.parse_headers(request_data)
        for line in unparsed_headers:
            try:
                req_method, resource,  http_version = unparsed_headers.pop().split()
            except ValueError:
                pass #need to handle this error, todo later
        parsed_headers['req_method'] = req_method
        parsed_headers['resource'] = resource
        parsed_headers['http-version'] = http_version

        return parsed_headers


    def generate_request(self, req_method, resource, server_addr, data_range=None):
        request_line = "%s /%s HTTP/1.1%s" % (req_method, resource, self.CRLF)

        if data_range is not None:
            data_range = "bytes=" + data_range
        header_dict = {
            'User-Agent': 'Python Script',
            'Host': '%s' % (server_addr),
            'Accept': '*/*',
            'Range': data_range
        }
        request = (request_line + "".join("%s: %s%s" % (key, value, self.CRLF) for key, value in header_dict.items() if value is not None) + self.CRLF)
        return request

class HttpResponse(HttpProtocol):

    def __init__(self, sock=None):
        super(HttpResponse, self).__init__(sock)

    def generate_response(self, total_content_length, resp_status_msg, content_range=None):
        response_line = 'HTTP/1.1 %s%s' % (resp_status_msg, self.CRLF)
        time_now = datetime.datetime.now()
        if content_range is not None:
            a, b = map(int, content_range.split('-'))
            content_length = b-a
            content_range = 'bytes %s/%s' %  (content_range, total_content_length)
        else:
            content_length = total_content_length
        send_headers = { 'Server' : 'Python Script',
                         'Content-Length' : content_length,
                         'Content-Range' : content_range,
                         'Accept-Ranges' : 'bytes',
                         'Date' : time_now.strftime("%d %b %Y, %H:%M:%S GMT") }
        send_data = ''.join("%s: %s%s" % (key, value, self.CRLF) for key, value in send_headers.items() if value is not None)

        return response_line + send_data + self.CRLF


    def parse_response(self, response_data):
        parsed_headers, unparsed_headers = self.parse_headers(response_data)
        for line in unparsed_headers:
            try:
                http_version, resp_code, resp_status_msg = unparsed_headers.pop().split(" ", maxsplit=2)
            except ValueError:
                raise ValueError("Header of unknow format recieved!")
        parsed_headers['http-version'] = http_version
        parsed_headers['resp_code'] = resp_code
        parsed_headers['resp_status_msg'] = resp_status_msg
        return parsed_headers

class SocketBuffer:

    WAIT_TIME = 10 #in seconds
    BLOCK_SIZE = 2048 #in bytes

    def __init__(self, sock):
        self.sock = sock
        self.data_recv = b''
        self.sock.settimeout(self.WAIT_TIME)

    def recv(self, length=0):
        try:
            msg_buffer = self.sock.recv(self.BLOCK_SIZE)
            self.data_recv += msg_buffer
        except socket.timeout:
            pass

        if length > 0:
            return_data = self.data_recv[:length]
            self.data_recv = self.data_recv[length:]
        else:
            return_data = None

        return return_data

    def empty_buffer(self):
        return_data = self.data_recv
        self.data_recv = b''
        return return_data

    def read_buffer(self, length):
        return_data = self.data_recv[:length]
        self.data_recv = self.data_recv[length:]
        return return_data
