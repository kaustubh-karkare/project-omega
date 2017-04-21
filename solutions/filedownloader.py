import socket
import tempfile
import logging
import urlparser
from concurrent.futures import ThreadPoolExecutor


BLOCK_SIZE = 1024
EOL = '\r\n'


def receive_data_from_host(client_socket, file_content=None):
    current_data = client_socket.recv(BLOCK_SIZE)
    status, _, data = current_data.partition(EOL)
    EOH = EOL + EOL
    header_data = ''
    previous_block = ''
    all_headers_received = False
    if EOH not in data:
        header_data = data
        previous_block = data
    else:
        headers, _, content = data.partition(EOH)
        header_data += headers
        all_headers_received = True
        if content is not '':
            file_content.write(content)
    while not all_headers_received:
        current_data = client_socket.recv(BLOCK_SIZE)
        if not current_data:
            break
        if EOH not in current_data:
            if EOH not in (current_data + previous_block):
                header_data += current_data
                previous_block = current_data
            else:
                all_headers_received = True
                headers, _, content = \
                    (previous_block + current_data).partition(EOH)
                if content is not '':
                    file_content.write(content)
        else:
            all_headers_received = True
            header, _, content = current_data.partition(EOH)
            header_data += header
            if content is not '':
                file_content.write(content)
    while True:
        content = client_socket.recv(BLOCK_SIZE)
        if not content:
            break
        file_content.write(content)
    headers = {}
    header_data = header_data.splitlines()
    for line in header_data:
        if not line:
            break
        key, _, value = line.partition(': ')
        headers[key] = value
    client_socket.close()
    if file_content is not None:
        file_content.flush()
    return (status, headers)


class FileDownloader:

    def __init__(self, url, threads, output_path):
        self.url_data = urlparser.parse_url(url)
        self.threads = threads
        self.output_path = output_path

    def start(self):
        # If protocol and port are missing, it is assumed to be a http request
        if (
            self.url_data.port is None or
            self.url_data.protocol is 'http' or
            self.url_data.port == 8080
        ):
            self.url_data = self.url_data._replace(port=80)
        self.initialize_download()
        downloaded_parts_name = self.download_parts()
        self.merge_downloaded_files(downloaded_parts_name)

    def initialize_download(self):
        headers = self.request_and_receive_reponse_headers()
        try:
            if (int(headers['Content-Length']) == 0):
                logging.warning('No data to download')
        except KeyError:
            logging.warning('Download size not available')
            self.threads = 1
        try:
            if (headers['Accept-Ranges'] != 'bytes'):
                self.threads = 1
        except KeyError:
            self.threads = 1

    def request_and_receive_reponse_headers(self):
        client_socket = socket.socket()
        try:
            client_socket.connect(
                (
                    self.url_data.host,
                    self.url_data.port
                )
            )
        except socket.error:
            logging.error('Client Socket connection could not be established')
            raise
        client_socket.send('HEAD %s HTTP/1.1%s' % (self.url_data.path, EOL))
        headers = {}
        headers['Host'] = self.url_data.host
        headers['Connection'] = 'close'
        # Add more headers when required
        for key, value in headers.iteritems():
            client_socket.send('%s: %s%s' % (key, value, EOL))
        client_socket.send(EOL)
        status, headers = receive_data_from_host(client_socket)
        return headers

    def download_parts(self):
        headers = self.request_and_receive_reponse_headers()
        try:
            content_length = int(headers['Content-Length'])
        except KeyError:
            content_length = 0
        each_part_size = int(content_length / self.threads)
        start_range = 0
        end_range = each_part_size
        downloaded_parts_name = []
        ii = 1
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while ii <= self.threads:
                if end_range >= content_length:
                    end_range = content_length - 1
                try:
                    download_file = tempfile.NamedTemporaryFile(delete=False)
                except:
                    logging.error('Temporary file could not be created')
                    raise
                downloaded_parts_name.append(download_file.name)
                client_socket = socket.socket()
                try:
                    client_socket.connect(
                        (
                            self.url_data.host,
                            self.url_data.port
                        )
                    )
                except socket.error:
                    logging.error('Client connection could not be made')
                    raise
                client_socket \
                    .send('GET %s HTTP/1.1%s' % (self.url_data.path, EOL))
                headers = {}
                headers['Host'] = self.url_data.host
                headers['Connection'] = 'close'
                # Add more headers when required
                for key, value in headers.iteritems():
                    client_socket.send('%s: %s%s' % (key, value, EOL))
                if self.threads != 1:
                    client_socket.send(
                        'Range: bytes=%s-%s%s' % (
                            str(start_range),
                            str(end_range),
                            EOL
                        )
                    )
                client_socket.send(EOL)
                executor.submit(
                        receive_data_from_host,
                        client_socket,
                        download_file
                )
                start_range = end_range + 1
                end_range = start_range + each_part_size
                ii += 1
        return downloaded_parts_name

    def merge_downloaded_files(self, downloaded_parts_name):
        try:
            output_file = open(self.output_path, 'w')
        except IOError:
            logging.error('Output file could not be created')
            raise
        for downloaded_file_name in downloaded_parts_name:
            downloaded_file = open(downloaded_file_name, 'r')
            output_file.write(downloaded_file.read())
            downloaded_file.close()
