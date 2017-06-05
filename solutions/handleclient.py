import os
import re
import socket
import threading
import urllib

BLOCK_SIZE = 1024
EOL = '\r\n'
EOH = EOL + EOL


class HandleClient(threading.Thread):
    status = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
        408: 'Request Timeout',
        501: 'Not Implemented',
    }
    pattern = r'([A-Z]+)\s+/*(\S*)\s+(HTTP/\d+\.\d+)'

    def __init__(self, client_socket, client_address, **kwargs):
        self.client_socket = client_socket
        request_timeout = kwargs.get('request_timeout', 5)
        self.client_socket.settimeout(request_timeout)
        self.request_timed_out = False
        super(HandleClient, self).__init__()

    def run(self):
        client_request, request_headers = self.recieve_request()
        response_headers = {}
        if self.request_timed_out:
            self.send_status_and_headers(408, response_headers)
            return
        if (
            client_request.get('method') is None or
            client_request.get('path') is None
        ):
            self.send_status_and_headers(400, response_headers)
            return

        requested_path = \
            os.path.join(os.getcwd(), client_request.get('path'))
        if (
            not os.path.isfile(requested_path) and
            not os.path.isdir(requested_path)
        ):
            self.send_status_and_headers(404, response_headers)
        elif client_request.get('method') == 'GET':
            if os.path.isfile(requested_path):
                self.send_file(requested_path, response_headers)
            else:
                default_path = \
                    os.path.join(requested_path, 'index.html')
                if os.path.isfile(default_path):
                    self.send_file(default_path, response_headers)
                else:
                    self.send_directory_content(
                        client_request['path'],
                        response_headers,
                    )
        else:
            self.send_status_and_headers(501, response_headers,)

    def recieve_request(self):
        client_request = dict()
        headers = dict()
        data = ''
        while EOL not in data:
            try:
                data += self.client_socket.recv(BLOCK_SIZE)
            except socket.timeout:
                self.request_timed_out = True
                return client_request, headers
        request_line, _, data = data.partition(EOL)
        try:
            client_request['method'], client_request['path'], \
                client_request['version'] = \
                re.match(HandleClient.pattern, request_line).groups()
        except AttributeError:
            return client_request, headers
        client_request['path'] = urllib.unquote(client_request['path'])
        while EOH not in data:
            try:
                data += self.client_socket.recv(BLOCK_SIZE)
            except socket.timeout:
                self.request_timed_out = True
                return client_request, headers
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
                EOL,
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
        self.client_socket.send('<html><body><ul>')
        for element in os \
                .listdir(os.path.join(os.getcwd(), directory_path)):
            self.client_socket.send(
                '<li><a href=' +
                os.path.join(
                    urllib.quote(directory_path),
                    urllib.quote(element)
                ) +
                '>' +
                element +
                '</a></li>'
            )
        self.client_socket.send('</ul></body></html>')
