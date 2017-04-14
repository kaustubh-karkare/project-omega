import os
import logging
from httprequestparser import parse_http_request
from tempfile import NamedTemporaryFile

BLOCK_SIZE = 1024
EOL = '\r\n'


class ReceiveAndProcessRequest:

    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.default_file = 'index.html'
        logging.info('Client connection received from:', self.client_address)
        try:
            http_request = self.client_socket.recv(BLOCK_SIZE)
        except:
            logging.error('Client request could not be received')
            raise
        self.process_request(http_request)
        self.client_socket.close()

    def process_request(self, http_request):
        http_request_data, headers = parse_http_request(http_request)
        http_request_data = (
            http_request_data._replace(
                path=os.path.join(
                    os.getcwd(),
                    http_request_data.path[1:]
                )
            )
        )
        logging.info('Path request by client is', http_request_data.path)

        if os.path.isfile(http_request_data.path):
            self.client_socket.send(
                'HTTP/1.1 200 OK' +
                EOL +
                'Content-Length: ' +
                str(
                    os.path.getsize(
                        http_request_data.path
                    )
                ) +
                EOL +
                EOL
            )
            requested_file = open(http_request_data.path, 'r')
            self.client_socket.send(requested_file.read())

        elif os.path.isdir(http_request_data.path):
            file_list = NamedTemporaryFile()
            default_file_path = (
                self.search_in_directory(
                    http_request_data.path,
                    file_list
                )
            )
            file_list.flush()
            self.client_socket.send('HTTP/1.1 200 OK' + EOL)
            self.client_socket.send('Content-Length: ')

            if default_file_path is None:
                file_list.seek(0)
                self.client_socket.send(
                    str(
                        os.path.getsize(
                            os.path.realpath(
                                file_list.name
                            )
                        )
                    ) +
                    EOL +
                    EOL
                )
                self.client_socket.send(file_list.read())
                file_list.close()

            else:
                send_default_file = open(default_file_path, 'r')
                self.client_socket.send(
                    str(
                        os.path.getsize(
                            default_file_path
                            )
                    ) +
                    EOL +
                    EOL
                )
                self.client_socket.send(EOL)
                self.client_socket.send(send_default_file.read())
                send_default_file.close()

        else:
            self.client_socket.send('HTTP/1.1 404 Not Found' + EOL + EOL)

    def search_in_directory(self, current_directory, file_list):
        if current_directory is None:
            return None
        for element in os.listdir(current_directory):
            current_path = os.path.join(current_directory, element)
            if os.path.isdir(current_path):
                default_file_path = (
                    self.search_in_directory(
                        current_path,
                        file_list
                    )
                )
                if default_file_path is not None:
                    return default_file_path
            else:
                file_name = element
                if file_name == self.default_file:
                    return current_path
                else:
                    file_list.write(file_name + '\n')
        return None
