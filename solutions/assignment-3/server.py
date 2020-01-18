import socket
import os
import re

class Server():

    def __init__(self, interface, port):
        self.interface = interface
        self.port = port
        self.homepage = 'http://' + interface + ':' + str(port)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.interface, self.port))
        self._handle_request()

    def stop(self):
        print("Exiting...")
        self.sock.close()

    def _handle_request(self):
        self.sock.listen(10)
        while True:
            print('Listening at ', self.homepage)
            try:
                self.conn_obj, self.client_addr = self.sock.accept()
            except KeyboardInterrupt:
                self.stop()
                break
            request_received = self._recvall()
            self._parse_request(request_received)
            print(self.resource, 'requested...')
            self._process_request()

    def _parse_request(self, request_data):
        headers = request_data.strip().split('\r\n')
        get, self.resource,  http_version = headers.pop(0).split()
        assert (http_version == 'HTTP/1.1')
        self.headers = dict()
        for header_line in headers:
            header, data = header_line.split(': ')
            self.headers[header] = data

    def _process_request(self):
        path = os.path.join(os.getcwd(), self.resource.strip('/'))
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'r') as upload_file:
                    print("sending index.html...")
                    send_data = (upload_file.read().encode())
                    resp_status_msg = '200 OK'
            else:
                print("generating directory listing and sending...")
                send_data = self._generate_index_of(self.resource).encode()
                resp_status_msg = '200 OK'

        elif os.path.isfile(self.resource.strip('/')):
            if os.path.exists(path):
                with open(path, 'rb') as upload_file:
                    print("sending file...")
                    send_data = (upload_file.read())
                    resp_status_msg = '200 OK'
            else:
                print("file not found, sending error response...")
                send_data = b''
                resp_status_msg = '404 Not Found'
        else:
            print("Bad Request")
            send_data = b''
            resp_status_msg = '400 Bad Request'

        content_length = len(send_data)
        self.conn_obj.sendall(self._generate_response_header(content_length, resp_status_msg) + send_data)

    def _generate_response_header(self, content_length, resp_status_code):
        header = ('HTTP/1.1 %s\r\n'
                  'Server: server.py\r\n'
                  'Content-Length: %s\r\n\r\n' % (resp_status_code, content_length))

        return header.encode()

    def _generate_index_of(self, location):
        regex_word = '</ul>\n'
        pattern_obj = re.compile(regex_word)

        head_template = ('<html>\n'
                         '<head>\n'
                         '<title>Directory listing for %s</title>\n'
                         '</head>\n' % (self.resource))

        body_template = ('<body>\n'
                         '<h1>Directory listing for %s</h1>\n'
                         '<hr>\n'
                         '<ul>\n'
                         '</ul>\n'
                         '<hr>\n'
                         '</body>\n'
                         '</html>' % (self.resource))

        for content in os.listdir('.' + location):
            link = os.path.join(self.homepage, self.resource, content)
            listing = '<li><a href=%s>%s</a></li>' % (link, content)
            seek = pattern_obj.search(body_template).start()
            body_template = body_template[:seek] + listing + '\n' + body_template[seek:]

        return head_template + body_template

    def _recvall(self):
        response_msg = ''
        msg_buffer = self.conn_obj.recv(1)
        response_msg += msg_buffer.decode()
        while response_msg[-4:] != '\r\n\r\n':
            msg_buffer = self.conn_obj.recv(1)
            response_msg += msg_buffer.decode()
        return response_msg
