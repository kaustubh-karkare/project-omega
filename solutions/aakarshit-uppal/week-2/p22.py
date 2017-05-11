#!/usr/bin/env python3
"""Download file from a link using socket connection.

Takes url as required argument in command line and destination path as
optional argument, shows success message on completion, including download
size, time and speed.

example::
prompt $ ./p22.py http://www.cse.iitd.ernet.in/~naveen/courses/CSL630/all.pdf
Finished Downloading all.pdf: Downloaded 2019.04 kB in 13.73 s at 147.07 kB/s
"""

import socket  # For socket
import sys  # For argv, exit
import os  # For handling directory
import threading  # For Thread
import time  # For time
# import shutil  # For get_terminal_size
import collections  # For named tuple
import logging  # For logging
from dl_exceptions import *  # For exceptions

# Logging specifications
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('download.log')
file_handler.setLevel(logging.DEBUG)
logging_format = '[%(asctime)s] [%(levelname)s]  %(name)s: %(message)s'
file_handler.setFormatter(logging.Formatter(logging_format))
logger.addHandler(file_handler)


class HttpRequestHandler:
    """Handles HTTP requests, from url to request to response."""

    def __init__(self, url, port=80, parts=4):
        """Set values of globals."""
        self.url = url
        self.buff_size = 2048
        self.port = port
        self.parts = parts
        self.fetched_data = {}

    def parse_url(self):
        """Extract host, port(if present), path and file name from URL."""
        url = self.url
        try:
            url = url.split('//', 1)[1]
        except IndexError:
            pass

        separation_point = url.find('/')
        self.host = url[:separation_point]
        try:
            self.port = int(self.host.split(':', 1)[1])
            self.host = self.host.split(':', 1)[0]
        except IndexError:
            pass
        self.path = url[separation_point:]
        self.file_name = url[url.rfind('/') + 1:]

        if self.file_name is '':
            logger.error('Nothing to download.')
            raise NoFileException

    def get_length(self):
        """Send HEAD request to extract content-length."""
        with socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM
                           ) as download_socket:

            # Create byte encoded request
            request = "HEAD {} HTTP/1.1\nHost: {}\n\n".format(self.path,
                                                              self.host)
            request = request.encode()

            # Send request and receive header
            download_socket.connect((self.host, self.port))
            download_socket.send(request)
            self.start_time = time.time()
            response = b''
            while(b'\r\n\r\n' not in response):
                response += download_socket.recv(self.buff_size)

            # Extract value of content_length attribute from response message
            content_length = response[response.find(b'Content-Length') + 15:]
            content_length = content_length[:content_length.find(b'\r')]
            try:
                self.length = int(content_length.decode())
            except ValueError:
                logger.error('Error: No internet/Invalid download link')
                raise ConnectionException
            if self.length == 0:
                logger.error('Error: Invalid link, Nothing to download')
                raise InvalidLinkException

            self.part_length = self.length // self.parts

    def fetch_data(self, part):
        """Fetch partial data corresponding to part using socket."""
        with socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM
                           ) as download_socket:

            # Create byte encoded request
            starting_byte = (part) * self.part_length
            if part == self.parts - 1:
                ending_byte = self.length
            else:
                ending_byte = (part + 1) * self.part_length - 1
            request = "GET {} HTTP/1.1\nHost: {}\nRange: bytes={}-{}\
                       \n\n".format(self.path,
                                    self.host,
                                    starting_byte,
                                    ending_byte)
            request = request.encode()

            # Send request and receive header+data
            download_socket.connect((self.host, self.port))
            download_socket.send(request)
            # self.start_time = time.time()
            logger.debug('Beginning download of part %d' % part)
            response = b''
            while(b'\r\n\r\n' not in response):
                response += download_socket.recv(self.buff_size)

            # Find bytes let to fetch
            data_beginning = response.find(b'\r\n\r\n') + 4
            initial_data = response[data_beginning:]
            bytes_to_fetch = self.part_length - len(initial_data)
            if part == self.parts - 1:
                bytes_to_fetch += self.length - self.parts * self.part_length
            # Fetch data in chunks
            fetched_data = b''
            while True:
                remaining_bytes = bytes_to_fetch - len(fetched_data)
                data_chunk = download_socket.recv(remaining_bytes)
                fetched_data += data_chunk
                if not data_chunk:
                    break
            self.finish_time = time.time()
            self.fetched_data[part] = initial_data + fetched_data
            logger.debug('Finished download of part %d' % part)

    def download_successful(self):
        """Verify completion of download."""
        received_data_length = 0
        for _, data in self.fetched_data.items():
            received_data_length += len(data)
        return received_data_length == self.length

    def _join_parts(self):
        # Join fetched data
        data = b''
        for part in range(self.parts):
            data += self.fetched_data[part]
        self.data = data
        logger.debug('Finished joining')

    def get_stats(self):
        """Return named tuple containing download stats."""
        kB_downloaded = (self.length / 1024)
        time_taken = (self.finish_time - self.start_time)
        download_speed = (kB_downloaded / time_taken)
        new_stats = collections.namedtuple('new_stats', ['kB_downloaded',
                                                         'time_taken',
                                                         'download_speed'])
        stats = new_stats(kB_downloaded, time_taken, download_speed)
        return stats

    def finish_up(self):
        """Finish up by joining parts and logging stats."""
        self._join_parts()
        stats = self.get_stats()
        stat_string = 'Downloaded %.2f kB in %.2f s at %.2f kB/s' % (
            stats.kB_downloaded, stats.time_taken, stats.download_speed)
        logger.info('Finished Downloading {}: {}'.format(self.file_name,
                                                         stat_string))


class Downloader:
    """Download file from a url."""

    def __init__(self, url=sys.argv[1], dl_path='.', port=80, parts=4):
        """Make request object and set path."""
        self.request = HttpRequestHandler(url, port=port, parts=parts)
        if len(sys.argv) > 2:
            dl_path = sys.argv[2]
        self.dl_path = dl_path
        self.parts = parts

    def download(self):
        """Download file data."""
        request = self.request
        request.parse_url()
        request.get_length()

        logger.debug('Beginning download from {}'.format(request.url))
        request.start_time = time.time()
        downloads = []
        for part in range(self.parts):
            downloads.append(threading.Thread(target=request.fetch_data,
                                              args=(part,)))
            downloads[part].start()
        while(threading.activeCount() > 1):
            time.sleep(0.01)

        if(request.download_successful()):
            logger.debug('Joining parts...')
            request.finish_up()
        self._create_file()

    def _create_file(self):
        # Create file from downloaded data.
        data_to_write = self.request.data
        file_with_path = '{}/{}'.format(self.dl_path, self.request.file_name)
        os.makedirs(os.path.dirname(file_with_path), exist_ok=True)
        logger.debug('Creating {}'.format(file_with_path))
        with open(file_with_path, 'wb') as downloaded_file:
            downloaded_file.write(data_to_write)
        logger.debug('Finished\n')


if __name__ == '__main__':
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    Downloader().download()
