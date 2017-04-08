import socket
import threading
import tempfile
import logging
import urlparser

BLOCK_SIZE = 1024


def receive_file_content_from_host(client_socket, download_file):
    while True:
        data = client_socket.recv(BLOCK_SIZE)
        if not data:
            break
        try:
            headers, content = data.split('\r\n\r\n')
            download_file.write(content)
        except:
            download_file.write(data)
    client_socket.close()
    download_file.flush()


class DownloadFile(threading.Thread):

    def __init__(self, url, threads, output_path):
        self.url = url
        self.threads = threads
        self.output_path = output_path
        threading.Thread.__init__(self)

    def run(self):
        self.url = urlparser.parse_url(self.url)
        self.pre_download_checks()
        self.download_files()

    def pre_download_checks(self):
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

    def https_headers_to_send_to_host(self):
        headers = {}
        headers['Host: '] = self.url.host
        headers['Connection: '] = 'close'
        # Add headers as per the requirement
        return headers

    def request_and_receive_reponse_headers(self):
        client_socket = socket.socket()
        try:
            client_socket.connect(
                (
                    self.url.host,
                    int(self.url.port)
                )
            )
        except:
            logging.error('Client Socket connection could not be established')
            raise
        line_break = '\r\n'
        headers_to_send_to_host = (self.https_headers_to_send_to_host())
        send_to_host = (
            'HEAD ' +
            self.url.path +
            ' HTTP/1.1' +
            line_break
        )
        for key, value in headers_to_send_to_host.iteritems():
            send_to_host += (
                key +
                value +
                line_break
            )
        send_to_host += line_break
        client_socket.send(send_to_host)
        # Request is made only for headers
        try:
            status, separator, received_headers = (
                client_socket.recv(BLOCK_SIZE).partition('\r\n')
            )
        except:
            logging.error('Host not responding')
            raise
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

    def download_files(self):
        headers = self.request_and_receive_reponse_headers()
        try:
            content_length = int(headers['Content-Length'])
        except:
            content_length = 0
        each_file_bytes = int(content_length / self.threads)
        start_range = 0
        end_range = each_file_bytes
        downloaded_file_names = []
        download_threads = []
        line_break = '\r\n'
        ii = 1
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
            downloaded_file_names.append(download_file.name)
            client_socket = socket.socket()
            try:
                client_socket.connect(
                    (
                        self.url.host,
                        int(self.url.port)
                    )
                )
            except:
                logging.error('Client connection could not be made')
                raise
            headers_to_send_to_host = self.https_headers_to_send_to_host()
            send_to_host = (
                'GET ' +
                self.url.path +
                ' HTTP/1.1' +
                line_break
            )
            for key, value in headers_to_send_to_host.iteritems():
                send_to_host += (
                    key +
                    value +
                    line_break
                )
            if (self.threads == 1):
                send_to_host += ('Range: bytes=0-' + line_break)
            else:
                send_to_host += (
                    'Range: bytes=' +
                    str(start_range) +
                    '-' +
                    str(end_range) +
                    line_break
                )
            send_to_host += line_break
            client_socket.send(send_to_host)
            download_threads.append(
                threading.Thread(
                    target=receive_file_content_from_host,
                    args=(
                        client_socket,
                        download_file
                    )
                )
            )
            download_threads[len(download_threads) - 1].start()
            start_range = end_range + 1
            end_range = start_range + each_file_bytes
            ii -= 1

        for thread_instance in download_threads:
            thread_instance.join()
        self.merge_downloaded_files(downloaded_file_names)

    def merge_downloaded_files(self, downloaded_file_names):
        try:
            output_file = open(self.output_path, 'w')
        except:
            logging.error('Output file could not be created')
            raise
        for downloaded_file_name in downloaded_file_names:
            downloaded_file = open(downloaded_file_name, 'r')
            downloaded_file.seek(0)
            output_file.write(downloaded_file.read())
            downloaded_file.close()
