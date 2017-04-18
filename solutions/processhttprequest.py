import os
import logging
import socket
import sys
from httprequestparser import parse_http_request

BLOCK_SIZE = 1024
EOL = '\r\n'


class ReceiveAndProcessRequest:

    def __init__(self, client_socket, client_address, base_directory):
        logging.info('Logger for client request')
        self.logger = logging.getLogger(__name__)
        self.client_socket = client_socket
        self.client_address = client_address
        self.base_directory = base_directory
        self.default_file = 'index.html'
        self.logger.info('Client connection:', self.client_address)
        self.client_socket.settimeout(1)
        http_request = ''
        while True:
            try:
                data = self.client_socket.recv(BLOCK_SIZE)
                if not data:
                    break
                http_request += data
            except socket.timeout:
                break
        self.process_request(http_request)
        self.client_socket.close()

    def process_request(self, http_request):
        status_code = None
        status_message = None
        http_request_data, headers = parse_http_request(http_request)
        http_request_data = (
            http_request_data._replace(
                path=os.path.join(
                    self.base_directory,
                    http_request_data.path[1:]
                )
            )
        )
        self.logger.info('Path request by client is', http_request_data.path)
        response_headers = {}
        file_to_send = None
        if os.path.isfile(http_request_data.path):
            file_to_send = http_request_data.path
            status_code = '200'
            status_message = 'OK'
            response_headers['Content-Length'] = (
                str(
                    os.path.getsize(
                        file_to_send
                    )
                )
            )

        elif os.path.isdir(http_request_data.path):
            default_file_path = (
                self.search_in_directory(
                    http_request_data.path,
                    )
                )
            status_code = '200'
            status_message = 'OK'
            if default_file_path is None:
                response_headers['Content-Length'] = (
                    str(
                        sys.getsizeof(
                            os.listdir(
                                http_request_data.path
                            )
                        )
                    )
                )

            else:
                response_headers['Content-Length'] = (
                    str(
                        os.path.getsize(
                            file_to_send
                        )
                    )
                )
                file_to_send = default_file_path
        else:
            status_code = '404'
            status_message = 'Not Found'

        self.client_socket.send(
            ' '.join(
                (
                    'HTTP/1.1',
                    status_code,
                    status_message,
                    EOL
                )
            )
        )
        for key, value in response_headers.iteritems():
            self.client_socket.send(key + ': ' + value + EOL)
        self.client_socket.send(EOL)
        if file_to_send is not None:
            with open(file_to_send, 'r') as send_content:
                content_of_file = send_content.read(BLOCK_SIZE)
                while content_of_file:
                    self.client_socket.send(content_of_file)
                    content_of_file = send_content.read(BLOCK_SIZE)
        elif status_code is '200':
            for element in os.listdir(http_request_data.path):
                self.client_socket.send(element + EOL)
        else:
            return

    def search_in_directory(self, current_directory):
        if current_directory is None:
            return None
        for element in os.listdir(current_directory):
            current_path = os.path.join(current_directory, element)
            if os.path.isfile(current_path):
                file_name = element
                if file_name == self.default_file:
                    return current_path
        return None
