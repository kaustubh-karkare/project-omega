import unittest
import tempfile
import os
import logging
from file_server import FileServer
from file_downloader import FileDownloader

class SocketTest(unittest.TestCase):
    BASE_ADDR = os.getcwd()

    def create_logger(self):
        log_level = logging.WARNING
        logger = logging.getLogger('file_downloader_logger')
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def test_simple_download(self):
         URL = 'http://olps.cgtransport.org/Esewa/img/ESEWA2.jpg'
         resource_size = 24963

         with tempfile.TemporaryDirectory() as TempDir:
             os.chdir(TempDir)
             logger = self.create_logger()
             downloader = FileDownloader(URL, "download_file", logger)
             downloader.download()

             self.assertTrue(os.stat("download_file").st_size == resource_size)
         os.chdir(self.BASE_ADDR)


    def test_multi_thread_download(self):
        URL = 'http://olps.cgtransport.org/Esewa/img/ESEWA2.jpg'
        resource_size = 24963

        with tempfile.TemporaryDirectory() as TempDir:
            os.chdir(TempDir)
            logger = self.create_logger()
            downloader = FileDownloader(URL, "download_file", logger, 4)
            downloader.download()
            self.assertTrue(os.stat("download_file").st_size == resource_size)
        os.chdir(self.BASE_ADDR)


if __name__ == "__main__":
    unittest.main()
