import socket
import os
import time

class FileServer():
    BLOCK_SIZE = 256 * 1000  # 256 kb

    def __init__(self, interface, port,  logger, server_location=os.getcwd()):
        self.interface = interface
        self.port = port
        self.homepage = 'http://' + interface + ':' + str(port)
        self.server_location = server_location
        self.logger = logger

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.interface, self.port))

    def run(self):
        try:
            self._handle_request()
        except KeyboardInterrupt:
            self.sock.close()

    def stop(self):
        self.logger.info("Exiting...")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def _handle_request(self):
        self.sock.listen(1)
        while True:
            self.logger.info('Listening at %s' % (self.homepage))
            try:
                self.conn_obj, self.client_addr = self.sock.accept()
            except KeyboardInterrupt:
                self.stop()
                break
            request_received = self._recvall()
            #print("Response received..")
            self._parse_request(request_received)
            self.logger.info('%s requested...' % (self.resource))
            if "Range" in self.headers:
                self._process_range_request()
            else:
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
        is_big_file = False

        path = os.path.join(self.server_location, self.resource.strip('/'))
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                upload_file = open(index_path, 'rb')

                    #data_chunk = upload_file.read(BLOCK_SIZE)
                self.logger.info("sending index.html...")
                    #send_data = (upload_file.read().encode())
                resp_status_msg = '200 OK'
                is_big_file = True
                content_length = os.stat(index_path).st_size
            else:
                self.logger.info("generating directory listing and sending...")
                send_data = self._generate_index_of(self.resource).encode()
                resp_status_msg = '200 OK'

        elif os.path.isfile(self.resource.strip('/')):
            if os.path.exists(path):
                upload_file = open(path, 'rb')
                #with open(path, 'rb') as upload_file:
                self.logger.info("sending file...")
                    #send_data = (upload_file.read())
                resp_status_msg = '200 OK'
                is_big_file = True
                content_length = os.stat(path).st_size
            else:
                self.logger.info("file not found, sending error response...")
                send_data = b''
                resp_status_msg = '404 Not Found'
        else:
            self.logger.info("Bad Request")
            send_data = b''
            resp_status_msg = '400 Bad Request'

        if is_big_file:
            self.conn_obj.sendall(self._generate_response_header(content_length, resp_status_msg))
            self._send_data_chunks(self.BLOCK_SIZE, upload_file)
        else:
            content_length = len(send_data)
            self.conn_obj.sendall(self._generate_response_header(content_length, resp_status_msg) + send_data)

    def _process_range_request(self):
        pass

    def _send_data_chunks(self, chunk_size, file_handler):
        while True:
            data_chunk = file_handler.read(chunk_size)
            if not data_chunk:
                break
            self.conn_obj.sendall(data_chunk)
            time.sleep(1)
        file_handler.close()

    def _generate_response_header(self, content_length, resp_status_code):
        header = ('HTTP/1.1 %s\r\n'
                  'Server: server.py\r\n'
                  'Content-Length: %s\r\n\r\n' % (resp_status_code, content_length))

        return header.encode()

    def _generate_index_of(self, location):
        head_template = ('<html>\n'
                         '<head>\n'
                         '<title>Directory listing for %s</title>\n'
                         '</head>\n' % (self.resource))


        all_lists = []
        for content in os.listdir('.' + location):
            link = os.path.join(self.homepage, self.resource, content)

            listing = '<li><a href=%s>%s</a></li>\n' % (link, content)
            all_lists.append(listing)
        all_lists = ''.join(all_lists)

        body_template = ('<body>\n'
                         '<h1>Directory listing for %s</h1>\n'
                         '<hr>\n'
                         '<ul>\n'
                         '%s'
                         '</ul>\n'
                         '<hr>\n'
                         '</body>\n'
                         '</html>' % (self.resource, all_lists))

        return head_template + body_template

    def _recvall(self):
        response_msg = ''
        msg_buffer = self.conn_obj.recv(1)
        response_msg += msg_buffer.decode()
        while response_msg[-4:] != '\r\n\r\n':
            msg_buffer = self.conn_obj.recv(1)
            response_msg += msg_buffer.decode()
        return response_msg
