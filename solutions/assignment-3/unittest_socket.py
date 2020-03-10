import unittest
import tempfile
import os
import logging
from file_server import FileServer
from file_downloader import FileDownloader

class HttpAppTest(unittest.TestCase):
    BASE_ADDR = os.getcwd()

    def create_logger(self, log_name):
        log_level = logging.WARNING
        logger = logging.getLogger(log_name)
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def create_dummy_file(self, file_size, file_name):
        with open(file_name, 'wb') as dummy_file:
            dummy_file.write(os.urandom(file_size))
        return os.stat(file_name).st_size


    def test_simple_download(self):
         URL = 'http://olps.cgtransport.org/Esewa/img/ESEWA2.jpg'

         resource_size = 24963

         with tempfile.TemporaryDirectory() as temp_dir:
             logger = self.create_logger('test_simple_download')
             download_file = os.path.join(temp_dir, 'download_file')
             downloader = FileDownloader(URL, download_file, logger)
             downloader.download()

             self.assertEqual(os.stat(download_file).st_size, resource_size)


    def test_multi_thread_download(self):
        URL = 'http://olps.cgtransport.org/Esewa/img/ESEWA2.jpg'
        resource_size = 24963

        with tempfile.TemporaryDirectory() as temp_dir:

            logger = self.create_logger('test_multi_thread_download')
            download_file = os.path.join(temp_dir, 'download_file')
            downloader = FileDownloader(URL, download_file, logger, 4)
            downloader.download()
            self.assertEqual(os.stat(download_file).st_size, resource_size)

    def test_setUp(self):
        FILE_NAME = 'temp_file'
        FILE_SIZE = 4 * 1000 * 1000
        SPEED_LIMIT = 256 * 1000 * 1
        HOST = "0.0.0.0"
        PORT = 0

        with tempfile.TemporaryDirectory() as temp_dir:
            logger = self.create_logger('test_simple_server_send')
            self.create_dummy_file(FILE_SIZE, FILE_NAME)
            server = FileServer(HOST, PORT, logger, temp_dir, SPEED_LIMIT)
            server.start()
            PORT = server.sock.getsockname()[1]
            URL = f"http://{HOST}:{PORT}/{FILE_NAME}"
            print(URL)
            downloader_single_thread = FileDownloader(URL, "simple_download", logger)
            downloader_single_thread.download()
            downloader_multi_thread = FileDownloader(URL, "multi_thread_download", logger, threads=4)
            downloader_multi_thread.download()
            server.stop()
            self.assertEqual(os.stat("simple_download").st_size, FILE_SIZE)
            self.assertEqual(os.stat("multi_thread_download").st_size, FILE_SIZE)

'''
    def test_simple_server_send(self):
        FILE_NAME = 'temp_file'
        FILE_SIZE = 4 * 1000 * 1000
        SPEED_LIMIT = 256 * 1000 * 1


        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            logger = self.create_logger('test_simple_server_send')
            file_size = self.create_dummy_file(FILE_SIZE, FILE_NAME)
            server = FileServer('0.0.0.0', 8000, logger, temp_dir, SPEED_LIMIT)
            server.start()
            downloader = FileDownloader(URL, "download_file", logger)
            downloader.download()
            server.stop()
            self.assertEqual(os.stat("download_file").st_size, file_size)
        os.chdir(self.BASE_ADDR)

    def test_non_blocking_server(self):

        FILE_NAME = 'temp_file'
        FILE_SIZE = 4 * 1000 * 1000
        SPEED_LIMIT = 256 * 1000 * 1
        HOST =
        URL = 'http://0.0.0.0:8000/' + FILE_NAME

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            logger = self.create_logger('test_non_blocking_server')
            file_size = self.create_dummy_file(FILE_SIZE, FILE_NAME)
            server = FileServer('0.0.0.0', 8000, logger, temp_dir, SPEED_LIMIT)
            server.start()
            #URL = os.path.join(temp_dir, FILE_NAME)
            downloader = FileDownloader(URL, "download_file", logger, threads=4)
            downloader.download()
            server.stop()
            self.assertEqual(os.stat("download_file").st_size, file_size)
        os.chdir(self.BASE_ADDR)
'''

if __name__ == "__main__":
    unittest.main()
