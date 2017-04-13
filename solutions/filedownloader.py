import socket
import tempfile
import logging
import urlparser
import concurrent.futures

BLOCK_SIZE = 1024
EOL = '\r\n'


def receive_data_from_host(client_socket, file_content):
    headers = ''
    previous_block = ''
    all_headers_received = False
    while True:
        current_data = client_socket.recv(BLOCK_SIZE)
        if not current_data:
            break
        if not all_headers_received:
            received_headers, separator, content = (
                current_data.partition(
                    EOL +
                    EOL
                )
            )
            if separator is None:
                received_headers, separator, content = (
                    (
                        previous_block +
                        current_data
                    ).partition(EOL + EOL)
                )
                if separator is None:
                    headers += current_data
                else:
                    all_headers_received = True
                    file_content.write(current_data)
            else:
                headers += received_headers
                file_content.write(content)
                all_headers_received = True
            previous_block = current_data
        else:
            file_content.write(current_data)
    client_socket.close()
    file_content.flush()
    return headers


class FileDownloader:

    def __init__(self, url, threads, output_path):
        self.url_data = urlparser.parse_url(url)
        self.threads = threads
        self.output_path = output_path

    def start(self):
        # If protocol and port are missing, it is assumed to be a https request
        if (
            self.url_data.port is None or
            self.url_data.protocol is 'https' or
            self.url_data.port is '8080'
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
        except:
            logging.warning('Download size not available')
            self.threads = 1
        try:
            if (headers['Accept-Ranges'] != 'bytes'):
                self.threads = 1
        except:
            self.threads = 1

    def get_request(self, https_method):
        send_to_host = (
            ' '.join(
                (
                    https_method,
                    self.url_data.path,
                    'HTTP/1.1'
                )
            )
        )
        send_to_host += EOL
        headers = {}
        headers['Host'] = self.url_data.host
        headers['Connection'] = 'close'
        # Add more headers when required
        for key, value in headers.iteritems():
            send_to_host += (
                ''.join(
                    (
                        key,
                        ': ',
                        value,
                        EOL
                    )
                )
            )
        return send_to_host

    def request_and_receive_reponse_headers(self):
        client_socket = socket.socket()
        try:
            client_socket.connect(
                (
                    self.url_data.host,
                    int(self.url_data.port)
                )
            )
        except:
            logging.error('Client Socket connection could not be established')
            raise
        send_to_host = self.get_request('HEAD')
        send_to_host += EOL
        client_socket.send(send_to_host)
        # Request is made only for headers
        content_file = tempfile.NamedTemporaryFile()
        received_headers = receive_data_from_host(client_socket, content_file)
        received_headers = received_headers.splitlines()
        headers = {}
        for line in received_headers:
            if not line:
                continue
            try:
                key, separator, value = line.partition(':')
                headers[key] = value[1:]
            except:
                logging.error('Error occurred while partitioning header')
                raise
        client_socket.close()
        return headers

    def download_parts(self):
        headers = self.request_and_receive_reponse_headers()
        try:
            content_length = int(headers['Content-Length'])
        except:
            content_length = 0
        each_part_size = int(content_length / self.threads)
        start_range = 0
        end_range = each_part_size
        downloaded_parts_name = []
        download_threads = []
        ii = 1
        executor = (
            concurrent.futures.ThreadPoolExecutor(
                max_workers=self.threads
            )
        )
        while ii <= self.threads:
            if (start_range > content_length - 1):
                # File already downloaded
                break
            if (end_range > content_length - 1):
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
                        int(self.url_data.port)
                    )
                )
            except:
                logging.error('Client connection could not be made')
                raise
            send_to_host = self.get_request('GET')
            if (self.threads == 1):
                send_to_host += ('Range: bytes=0-' + EOL)
            else:
                send_to_host += (
                    'Range: bytes=' +
                    str(start_range) +
                    '-' +
                    str(end_range) +
                    EOL
                )
            send_to_host += EOL
            client_socket.send(send_to_host)
            download_threads.append(
                executor.submit(
                    receive_data_from_host,
                    client_socket,
                    download_file
                )
            )
            start_range = end_range + 1
            end_range = start_range + each_part_size
            ii -= 1

        concurrent.futures.wait(download_threads)
        return downloaded_parts_name

    def merge_downloaded_files(self, downloaded_parts_name):
        try:
            output_file = open(self.output_path, 'w')
        except:
            logging.error('Output file could not be created')
            raise
        for downloaded_file_name in downloaded_parts_name:
            downloaded_file = open(downloaded_file_name, 'r')
            downloaded_file.seek(0)
            output_file.write(downloaded_file.read())
            downloaded_file.close()
