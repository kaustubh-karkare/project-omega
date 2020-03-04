import socket
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from shutil import copyfileobj
import utility


class FileDownloader:
    """
    Downloads the resource from a given url and saves it in a file
    with name specified.

    :param url: url of resource to download
    :param download_path: file name to save download as
    :param logger: logger object used for debugging and other running information
    :param threads: number of parts to download specified resource in
    """

    def __init__(self, url, save_as, logger, threads=1):
        self.url = url
        self.download_path = os.path.join(os.getcwd(), save_as)
        self.threads = threads
        self.logger = logger
        self.host, self.port, self.resource = utility.HttpProtocol.find_server_and_resouce(url)

    def download(self):
        """
        Downloads requested resources in either multiple parts(if threads more than one)
        or singly.

        If the file is being downloaded in multiple parts, the script creates multiple
        threads and downloads file part sizes and then stitches all the files into one
        main file.
        """
        if self.threads > 1:
            file_size = self._get_file_size(self.host, self.port, self.resource, self.logger)
            download_ranges = self._compute_request_ranges(file_size, self.threads)
            handlers = []
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for index in range(len(download_ranges)):
                    filename = self.download_path + ("%d" % (index+1))
                    handler = DownloadHandler(self.host, self.port, self.resource, self.logger, data_ranges=download_ranges[index], download_path=filename)
                    handlers.append(handler)
                    executor.submit(handler.download)
            time_taken = time.time() - start_time
            self._stitch_downloads(self.download_path, [handler.download_path for handler in handlers])

        else:
            #self.logger.info("Download started")
            start_time = time.time()
            self._download_single()
            time_taken = time.time() - start_time
        self.logger.info("Download completed")
        self.logger.info("Download time: %f sec" % (time_taken)) #now possibly contains extra time because of artificially added wait

    def _stitch_downloads(self, download_path, download_files):
        with open(download_path, 'wb') as main_file:
            for download_file in download_files:
                with open(download_file, 'rb') as temp_file:
                    copyfileobj(temp_file, main_file)
                os.remove(download_file)

    def _download_single(self):
        download_obj = DownloadHandler(self.host, self.port, self.resource, self.logger, download_path=self.download_path)
        download_obj.download()

    @staticmethod
    def _get_file_size(host, port, resource, logger):
        downloader = DownloadHandler(host, port, resource, logger)
        headers = downloader.headers_request()
        logger.info("Analyzing header data...")
        assert (headers['resp_code'] == '200')
        return int(headers['Content-Length'])

    @staticmethod
    def _compute_request_ranges(content_length, parts):
        '''
        Calculates ranges to download the resource according to
        number of parts specified
        '''

        data_ranges = list()
        start = 0
        part_size = int((content_length) / parts)
        iters = parts - 1 if content_length % parts != 0 else parts

        for _ in range(iters):
            data_ranges.append(str(start) + "-" + str(start+part_size-1))
            start += part_size
        if start < content_length:
            data_ranges.append(str(start) + "-" + str(content_length-1))
        return data_ranges


class DownloadHandler():
    """
    Handles downloading specified resource

    :param host: host address of the server to download resource from
    :param port: port to use
    :param resource: resource path in the server
    :param data_ranges: range of bytes to download, defaults to None if not provided
    """

    def __init__(self, host, port, resource, logger, data_ranges=None, download_path=None):
        self.host = host
        self.port = port
        self.resource = resource
        self.download_path = self._generate_filename(download_path)
        self.logger = logger
        self.data_ranges = data_ranges

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.logger.debug("Downloader script address: %s" % (str(self.sock.getsockname())))
        self.logger.debug("Connected to: %s" % (str(self.sock.getpeername())))
        self.buffer = utility.SocketBuffer(self.sock)
        self.request_util = utility.HttpRequest(socket_buffer=self.buffer)
        self.response_util = utility.HttpResponse(socket_buffer=self.buffer)

    def download(self):
        self._send("GET")
        self._receive()
        self.sock.close()

    def headers_request(self):
        self._send("HEAD")
        #time.sleep(self.buffer.WAIT_TIME)
        headers = self.response_util.parse_response()
        self.sock.close()
        return headers

    def _send(self, req_method):
        request = self.request_util.generate_request(req_method, self.resource, self.host, self.data_ranges)
        self.logger.debug("Request generated:\n%s" % (request))
        self.sock.sendall(request.encode())
        time.sleep(self.buffer.WAIT_TIME)
        self.logger.info("Request sent")

    def _receive(self):
        #header_data = self.request_util.get_headers()
        #self.logger.debug("Header received:\n%s" % (header_data))
        # expect 206 Partial Content response if range request issued otherwise expect normal response 200
        expected_resp_code = "206" if self.data_ranges is not None else "200"
        self.logger.info("receving header data...")
        self.received_headers = self.response_util.parse_response()
        self.logger.debug("Header received:\n%s" % (self.received_headers))
        assert (self.received_headers[self.response_util.RESP_CODE] == expected_resp_code)
        assert (self.received_headers[self.response_util.HTTP_VERSION] == 'HTTP/1.1')
        self.request_util.sb.download_to(self.download_path, int(self.received_headers['Content-Length']))

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    @staticmethod
    def _generate_filename(filepath):
        if filepath is None:
            return os.path.join(os.getcwd(), "download_file")
        if not os.path.exists(filepath):
            return filepath
        else:
            i = 1
            while os.path.exists(filepath + str(i)):
                i += 1
            return filepath + str(i)
