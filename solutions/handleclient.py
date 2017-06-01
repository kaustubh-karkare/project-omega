import os
import re
import socket
import threading

BLOCK_SIZE = 1024
EOL = '\r\n'
EOH = EOL + EOL


class HandleClient(threading.Thread):
    status = {}
    status[200] = 'OK'
    status[400] = 'Bad Request'
    status[404] = 'Not Found'
    status[501] = 'Not Implemented'

    def __init__(self, client_socket, client_address, **kwargs):
        self.client_socket = client_socket
        self.client_socket.settimeout(1)
        threading.Thread.__init__(self)

    def run(self):
        client_request, request_headers = self.recieve_request()
        response_headers = {}
        if client_request.get('method') == 'GET':
            requested_path = \
                os.path.join(os.getcwd(), client_request.get('path'))
            if client_request.get('path') is None:
                self.send_status_and_headers(400, response_headers)
            elif os.path.isfile(requested_path):
                self.send_file(requested_path, response_headers)
            elif os.path.isdir(requested_path):
                default_path = \
                    os.path.join(requested_path, 'index.html')
                if os.path.isfile(default_path):
                    self.send_file(default_path, response_headers)
                else:
                    self.send_directory_content(
                        client_request['path'],
                        response_headers
                    )
            else:
                self.send_status_and_headers(404, response_headers)
        elif client_request.get('method') is None:
            self.send_status_and_headers(400, response_headers)
        else:
            self.send_status_and_headers(501, response_headers)

    def recieve_request(self):
        client_request = dict()
        headers = dict()
        data = ''
        while EOL not in data:
            try:
                data += self.client_socket.recv(BLOCK_SIZE)
            except socket.timeout:
                break
        request_line, _, data = data.partition(EOL)
        pattern = r'([A-Z]+)\s+/*(\S*)\s+(HTTP/\d+\.\d+)'
        try:
            request_line = re.match(pattern, request_line).groups()
        except AttributeError:
            return client_request, headers
        client_request['method'] = request_line[0]
        client_request['path'] = request_line[1]
        client_request['version'] = request_line[2]
        while EOH not in data:
            try:
                data += self.client_socket.recv(BLOCK_SIZE)
            except socket.timeout:
                break
        data = data.splitlines()
        headers = {}
        for line in data:
            key, _, value = line.partition(': ')
            headers[key] = value
        return client_request, headers

    def send_status_and_headers(self, status_code, headers):
        self.client_socket.send(
            'HTTP/1.1 %d %s%s' % (
                status_code,
                HandleClient.status[status_code],
                EOL
            )
        )
        for key, value in headers.items():
            self.client_socket.send('%s: %s%s' % (key, value, EOL))
        self.client_socket.send(EOL)

    def send_file(self, file_path, headers):
        headers['Content-Length'] = os.path.getsize(file_path)
        self.send_status_and_headers(200, headers)
        with open(file_path, 'r') as requested_file:
            while True:
                data = requested_file.read(BLOCK_SIZE)
                if not data:
                    break
                self.client_socket.send(data)

    def send_directory_content(self, directory_path, headers):
        self.send_status_and_headers(200, headers)
        for element in os.listdir(os.path.join(os.getcwd(), directory_path)):
            self.client_socket.send(
                "<a href=%s> %s </a> %s <br>" % (
                    (
                        os.path.join(
                            directory_path.replace(' ', '%20'),
                            element.replace(' ', '%20')
                        )
                    ),
                    element,
                    EOL
                )
            )
