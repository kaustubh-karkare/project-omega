#!/usr/bin/env python3
"""Download file from a link using socket connection.

Takes url as required argument in command line and destination path as
optional argument, shows progress durin download and succes message on
completion, including download size, time and speed.

example::
prompt $ ./p22.py http://www.cse.iitd.ernet.in/~naveen/courses/CSL630/all.pdf
[############################################################]100%
Finished Downloading all.pdf: Downloaded 2019.04 kB in 13.73 s at 147.07 kB/s
"""

import socket  # For soket
import sys  # For argv, exit
import os  # For handling directory
import threading  # For Thread
import time  # For time
import shutil  # For get_terminal_size
import collections  # For named tuple


class _HttpRequestHandler:
    # Handles HTTP requests, from url to request to response

    def __init__(self, url):
        # Set url and buffer size
        self.url = url
        self.buff_size = 2048

    def _handle_url(self):
        # Extract host, path and file name from URL
        url = self.url
        try:
            url = url.split('//', 1)[1]
        except IndexError:
            pass

        separation_point = url.find('/')
        self.host = url[:separation_point]
        self.path = url[separation_point:]
        self.file_name = url[url.rfind('/'):][1:]

        if self.file_name is '':
            print('Error: Nothing to download.')
            sys.exit(0)

    def _create_request(self):
        # Create byte encoded request
        self.request = "GET %s HTTP/1.1\nHost: %s\n\n" % (self.path, self.host)
        self.request = self.request.encode()

    def _fetch_data(self):
        # Fetch data using sockets
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dlsocket:

            # Send request and receive message+data
            dlsocket.connect((self.host, 80))
            dlsocket.send(self.request)
            self.start_time = time.time()
            response = dlsocket.recv(self.buff_size)

            # Extract value of content_length attribute from response message
            content_length = response[response.find(b'Content-Length') + 15:]
            content_length = content_length[:content_length.find(b'\r')]
            try:
                self.length = int(content_length.decode())
            except ValueError:
                print('Error: No internet/Invalid download link')
                sys.exit(0)
            if self.length == 0:
                print('Error: Invalid link, Nothing to download')
                sys.exit(0)

            # Find bytes let to fetch
            file_beginning = response.find(b'\r\n\r\n') + 4
            initial_data = response[file_beginning:]
            bytes_to_fetch = self.length - len(initial_data)

            # Elements to be used to show progress
            self.progress = 0
            self.received_data_length = len(initial_data)
            self.progress_thread = threading.Thread(target=self._showProgress)
            self.progress_thread.start()

            # Fetch data in chunks
            fetched_data = b''
            while len(fetched_data) < bytes_to_fetch:
                remaining_bytes = bytes_to_fetch - len(fetched_data)
                data_chunk = dlsocket.recv(remaining_bytes)
                fetched_data += data_chunk
                self.received_data_length += len(data_chunk)
                if not data_chunk:
                    break
            self.finish_time = time.time()
            self.fetched_data = initial_data + fetched_data

            # Wait for progress thread
            if self.progress_thread.isAlive():
                time.sleep(0.01)

            # Verify completion of download
            if self._download_successful():
                self._finish_up()
            else:
                print('Error: Download Failed. Try Again...')

    def _showProgress(self):
        # Show progress in terms of graphical bar and percentage
        while not self.progress > 99:
            total = self.length
            done = self.received_data_length
            scale = shutil.get_terminal_size()[0] - 30
            self.progress = int((done * 100) / total)
            scaled_progress = int(self.progress * scale / 100)
            time.sleep(0.001)
            sys.stdout.write("\b" * (scale + 5))
            progress_str = '[{}{}]{}%'.format('#' * scaled_progress,
                                              ' ' * (scale - scaled_progress),
                                              self.progress)
            print(progress_str, end='')
        print()

    def _download_successful(self):
        # Verify completion of download
        return self.received_data_length == self.length

    def _get_stats(self):
        # Return named tuple containing download stats
        kB_downloaded = (len(self.fetched_data) / 1024)
        time_taken = (self.finish_time - self.start_time)
        download_speed = (kB_downloaded / time_taken)
        new_stats = collections.namedtuple('new_stats', ['kB_downloaded',
                                                         'time_taken',
                                                         'download_speed'])
        stats = new_stats(kB_downloaded, time_taken, download_speed)
        return stats

    def _finish_up(self):
        # Perform finishing tasks
        stats = self._get_stats()
        stat_string = 'Downloaded %.2f kB in %.2f s at %.2f kB/s' % (
            stats.kB_downloaded, stats.time_taken, stats.download_speed)
        print('Finished Downloading {}: {}'.format(self.file_name,
                                                   stat_string))


class Downloader:
    """Download files from links using passed in command line."""

    def __init__(self, url=sys.argv[1], dl_path='.'):
        """Make request object and set url and path."""
        self.request = _HttpRequestHandler(url)
        if len(sys.argv) > 2:
            dl_path = sys.argv[2]
        self.dl_path = dl_path

    def download(self):
        """Download file data."""
        request = self.request
        request._handle_url()
        request._create_request()
        request._fetch_data()
        self._create_file()

    def _create_file(self):
        # Create file from downloaded data.
        data_to_write = self.request.fetched_data
        file_with_path = '{}/{}'.format(self.dl_path, self.request.file_name)
        os.makedirs(os.path.dirname(file_with_path), exist_ok=True)
        with open(file_with_path, 'wb') as downloaded_file:
            downloaded_file.write(data_to_write)


if __name__ == '__main__':
    ob = Downloader()
    ob.download()
