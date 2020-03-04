import re
import datetime
import socket
import typing
import time

class HttpProtocol:

    CRLF = '\r\n'
    HEADER_LINE = 'header_line'

    def __init__(self, socket_buffer=None):
        self.sb = socket_buffer

    def get_headers(self, timeout_flag=False):
        '''
        Receive header data from socket
        '''
        headers = {}
        while True:
            line = self.sb.readLine(timeout_flag)
            print("GOT:", (line))
            if line == '':
                #print("we done")
                break
            key, _, value = line.partition(": ")
            if (_ == '') and (value == ''):
                headers[self.HEADER_LINE] = key
            else:
                headers[key] = value

        return headers

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

    REQ_METHOD = 'req_method'
    RESOURCE = 'resource'
    HTTP_VERSION = 'http_version'

    def __init__(self, *args, **kwargs):
        super(HttpRequest, self).__init__(*args, **kwargs)

    def parse_request(self):
        headers = self.get_headers(True)
        req_method, resource,  http_version = headers[self.HEADER_LINE].split()
        headers[self.REQ_METHOD] = req_method
        headers[self.RESOURCE] = resource
        headers[self.HTTP_VERSION] = http_version

        return headers


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

    HTTP_VERSION = 'http_version'
    RESP_CODE = 'resp_code'
    RESP_STATUS_MSG = 'resp_status_msg'

    def __init__(self, *args, **kwargs):
        super(HttpResponse, self).__init__(*args, **kwargs)

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


        self.sb.sock.sendall((response_line + send_data + self.CRLF).encode())
        time.sleep(self.sb.WAIT_TIME)


    def parse_response(self):
        headers = self.get_headers(True)
        #print("HEADERS:", headers)
        http_version, resp_code, resp_status_msg = headers[self.HEADER_LINE].split(" ", maxsplit=2)
        headers[self.HTTP_VERSION] = http_version
        headers[self.RESP_CODE] = resp_code
        headers[self.RESP_STATUS_MSG] = resp_status_msg
        return headers

class SocketBuffer:

    WAIT_TIME = 5 #in seconds
    BLOCK_SIZE = 2048 #in bytes
    CRLF = '\r\n'

    def __init__(self, sock):
        self.sock = sock
        self.data_buffer = b''
        #self.sock.settimeout(self.WAIT_TIME)

    def readLine(self, timeout=False):

        if self.CRLF.encode() in self.data_buffer:
            return_data = ''
            seek = self.data_buffer.find(self.CRLF.encode())
            return_data = self.data_buffer[:seek].decode()
            self.data_buffer = self.data_buffer[seek+2:]
            return return_data

        if timeout and (self.sock.gettimeout != self.WAIT_TIME):
            self.sock.settimeout(self.WAIT_TIME)
        elif not timeout:
            self.sock.settimeout(None)

        msg_buffer = b''
        #print(self.sock.getsockname(), "is blocking:", self.sock.getblocking())
        try:
            #print("im stuck in recv of:", self.sock.getsockname(), "timout:", self.sock.gettimeout())
            msg_buffer = self.sock.recv(self.BLOCK_SIZE)

        except socket.timeout as e:
            err = e.args[0]
            if err =='time out':
                time.sleep(1)
                #print('recv timed out for', self.sock.getsockname())
        except socket.error as e:
            print(e, self.sock.getsockname())

        return_data = ''
        self.data_buffer += msg_buffer
        seek = self.data_buffer.find(self.CRLF.encode())
        return_data = self.data_buffer[:seek].decode()
        self.data_buffer = self.data_buffer[seek+2:]

        #print("return recv data for", self.sock.getsockname(), ":", return_data)
        return return_data

    def upload_from(self, file_handler, seek_start, seek_end, speed_bps=2048):
        file_handler.seek(seek_start)

        while file_handler.tell() <= seek_end:

            data_chunk = file_handler.read(min(speed_bps, seek_end - file_handler.tell() + 1))
            if not data_chunk:
                break
            self.sock.sendall(data_chunk)
            time.sleep(1)

    def download_to(self, file_handle, size):
        download_length = 0

        with open(file_handle, 'wb') as download_file:
            buffer_data = self.empty_buffer()
            download_file.write(buffer_data)

            while download_length < size:
                try:
                    data_recv = self.sock.recv(self.BLOCK_SIZE)

                except socket.timeout:
                    #print()
                    #download_file.write(data_recv)
                    return None
                if not data_recv:
                    return None
                #print("GOT:", data_recv)
                download_length += len(data_recv)
                download_file.write(data_recv)

    def empty_buffer(self):
        return_data = self.data_buffer
        self.data_buffer = b''
        return return_data

    def read_buffer(self, length):
        return_data = self.data_buffer[:length]
        self.data_buffer = self.data_buffer[length:]
        return return_data
