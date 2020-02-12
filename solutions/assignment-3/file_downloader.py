import socket
import os
import threading
import time
from shutil import copyfileobj
import utility


class FileDownloader:
    """
    Downloads the resource from a given url and saves it in a file
    with name specified.

    :param url: url of resource to download
    :param save_as: file name to save download as
    :param logger: logger object used for debugging and other running information
    :param threads: number of parts to download specified resource in
    """

    def __init__(self, url, save_as, logger, threads=1):
        self.url = url
        self.save_as = save_as
        self.threads = threads
        self.logger = logger
        self.host, self.port, self.resource = utility.HttpProtocol.find_server_and_resouce(url)


    def _analyze_header_data(self):
        download_obj = DownloadHandler(self.host, self.port, self.resource, self.logger)
        header_data = download_obj.headers_request()
        self.logger.info("Analyzing header data...")
        temp_response_util = utility.HttpResponse()
        headers = temp_response_util.parse_response(header_data)
        assert (headers['resp_code'] == '200')
        self.data_ranges = utility.HttpProtocol.compute_request_ranges(int(headers['Content-Length']), self.threads)
        self.logger.debug("Byte ranges created: %s" % (self.data_ranges))
        self.logger.info("Script ready to download!")

    def download(self):
        """
        Downloads requested resources in either multiple parts(if threads more than one)
        or singly.

        If the file is being downloaded in multiple parts, the script creates multiple
        threads and downloads file part sizes and then stitches all the files into one
        main file.
        """
        if self.threads > 1:
            self._analyze_header_data()
            self.logger.info("Download started")
            start_time = time.time()
            self._download_multi()
            time_taken = time.time() - start_time
            self._stitch_downloads()
        else:
            self.logger.info("Download started")
            start_time = time.time()
            self._download_single()
            time_taken = time.time() - start_time
        self.logger.info("Download completed")
        self.logger.info("Download time: %f sec" % (time_taken))

    def _stitch_downloads(self):
        with open(self.save_as, 'wb') as main_file:
            for download_file in self.download_files:
                with open(download_file, 'rb') as temp_file:
                    copyfileobj(temp_file, main_file)
                os.remove(download_file)

    def _download_multi(self):
        threads = list()
        download_objs = dict()
        for index in range(len(self.data_ranges)):
            filename = self.save_as + ("%d" % (index))
            download_objs[filename] = DownloadHandler(self.host, self.port, self.resource, self.logger, data_ranges=self.data_ranges[index], save_as=filename)
            thread_obj = threading.Thread(target=download_objs[filename].download)
            threads.append(thread_obj)
            thread_obj.start()
        for thread in threads:
            thread.join()

        self.download_files = download_objs.keys()

    def _download_single(self):
        download_obj = DownloadHandler(self.host, self.port, self.resource, self.logger, save_as=self.save_as)
        download_obj.download()

class DownloadHandler():
    """
    Handles downloading specified resource

    :param host: host address of the server to download resource from
    :param port: port to use
    :param resource: resource path in the server
    :param data_ranges: range of bytes to download, defaults to None if not provided
    """

    def __init__(self, host, port, resource, logger, data_ranges=None, save_as='download_file'):
        self.host = host
        self.port = port
        self.resource = resource
        self.save_as = save_as
        self.logger = logger
        self.data_ranges = data_ranges

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.request_util = utility.HttpRequest(self.sock)
        self.response_util = utility.HttpResponse(self.sock)

    def download(self):
        self._send("GET")
        self._receive()
        self.sock.close()

    def headers_request(self):
        self._send("HEAD")
        headers = self.request_util.get_headers()
        self.sock.close()
        return headers

    def _send(self, req_method):
        request = self.request_util.generate_request(req_method, self.resource, self.host, self.data_ranges)
        self.logger.debug("Request generated:\n%s" % (request))
        self.sock.sendall(request.encode())

    def _receive(self):
        header_data = self.request_util.get_headers()
        self.logger.debug("Header received:\n%s" % (header_data))
        # expect 206 Partial Content response if range request issued otherwise expect normal response 200
        expected_resp_code = "206" if self.data_ranges is not None else "200"
        self.received_headers = self.response_util.parse_response(header_data)
        assert (self.received_headers['resp_code'] == expected_resp_code)
        assert (self.received_headers['http-version'] == 'HTTP/1.1')
        self.response_util.download_payload(self.save_as, int(self.received_headers['Content-Length']))

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
