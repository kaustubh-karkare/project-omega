import socket
import tempfile
import logging
import urlparser
from concurrent.futures import ThreadPoolExecutor


BLOCK_SIZE = 1024
EOL = '\r\n'
EOH = EOL + EOL


class FileDownloader:

    def __init__(self, url, threads, output_path):
        self.url_data = urlparser.parse_url(url)
        self.threads = threads
        self.output_path = output_path

    def start(self):
        # If protocol and port are missing, it is assumed to be a http request
        if (
            self.url_data.port is None or
            self.url_data.protocol is 'http'
        ):
            self.url_data = self.url_data._replace(port=80)
        downloaded_parts_reference = self.download_parts()
        self.merge_downloaded_files(downloaded_parts_reference)

    def send_request(
        self,
        http_method,
        client_socket,
        start_range=0,
        end_range=0
    ):
        client_socket \
            .send('%s %s HTTP/1.1%s' % (http_method, self.url_data.path, EOL))
        headers = {}
        headers['Host'] = self.url_data.host
        headers['Connection'] = 'close'
        if self.threads != 1:
            headers['Range'] = \
                'bytes=%s-%s' % (str(start_range), str(end_range))
        # Add more headers when required
        for key, value in headers.iteritems():
            client_socket.send('%s: %s%s' % (key, value, EOL))
        client_socket.send(EOL)

    def receive_data_from_host(self, client_socket, file_content=None):
        current_data = ''
        while True:
            current_data += client_socket.recv(BLOCK_SIZE)
            if EOL in current_data:
                break
        status, _, current_data = current_data.partition(EOL)
        while True:
            current_data += client_socket.recv(BLOCK_SIZE)
            if EOH in current_data:
                break
        header_data, _, current_data = current_data.partition(EOH)
        while True:
            current_data += client_socket.recv(BLOCK_SIZE)
            if not current_data:
                break
            file_content.write(current_data)
            current_data = ''
        headers = {}
        header_data = header_data.splitlines()
        for line in header_data:
            key, _, value = line.partition(': ')
            headers[key] = value
        if file_content is not None:
            file_content.flush()
        client_socket.close()
        return (status, headers)

    def request_and_receive_reponse_headers(self):
        client_socket = socket.socket()
        try:
            client_socket.connect((self.url_data.host, self.url_data.port))
        except socket.error:
            logging.error('Client Socket connection could not be established')
            raise
        self.send_request('HEAD', client_socket)
        status, headers = self.receive_data_from_host(client_socket)
        print(headers)
        return headers

    def download_parts(self):
        headers = self.request_and_receive_reponse_headers()
        content_length = headers.get('Content-Length')
        if content_length is None:
            content_length = 0
            self.threads = 1
        else:
            content_length = int(content_length)
        if headers.get('Accept-Ranges') is None:
            self.threads = 1
        each_part_size = int(content_length / self.threads)
        start_range = 0
        end_range = each_part_size
        downloaded_parts_reference = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for ii in range(self.threads):
                if end_range >= content_length:
                    end_range = content_length - 1
                try:
                    download_file = tempfile.NamedTemporaryFile(delete=False)
                except:
                    logging.error('Temporary file could not be created')
                    raise
                downloaded_parts_reference.append(download_file)
                client_socket = socket.socket()
                try:
                    client_socket \
                        .connect((self.url_data.host, self.url_data.port))
                except socket.error:
                    logging.error('Client connection could not be made')
                    raise

                self.send_request(
                    'GET',
                    client_socket,
                    start_range,
                    end_range
                )
                executor.submit(
                    self.receive_data_from_host,
                    client_socket,
                    download_file
                )
                start_range = end_range + 1
                end_range = start_range + each_part_size
        return downloaded_parts_reference

    def merge_downloaded_files(self, downloaded_parts_reference):
        try:
            output_file = open(self.output_path, 'w')
        except IOError:
            logging.error('Output file could not be created')
            raise
        for downloaded_part_reference in downloaded_parts_reference:
            downloaded_part_reference.seek(0)
            output_file.write(downloaded_part_reference.read())
            downloaded_part_reference.close()
