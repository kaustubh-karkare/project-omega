import unittest
import hashlib
import os
import tempfile
from contextlib import contextmanager
from urlFileDownloader import UrlFileDownloader
from exception import InvalidUrl

CHUNK_SIZE = 4096


@contextmanager
def tempdir(dirname):
    oldpath = os.getcwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(oldpath)


class TestUrlFileDownloader(unittest.TestCase):

    def download_and_match_hash(self, urlFileDownloader: UrlFileDownloader, expected_hash_content: bytes):
        hash = hashlib.sha256()
        with tempfile.TemporaryDirectory() as tmpdirname:
            with tempdir(tmpdirname):
                urlFileDownloader.download()
                with open(urlFileDownloader.download_file, 'rb') as file:
                    while True:
                        data = file.read(CHUNK_SIZE)
                        if not data:
                            break
                        hash.update(data)
        self.assertEqual(hash.digest(), expected_hash_content)

    def test_small_txt_file_download_having_https_scheme(self):
        urlFileDownloader = UrlFileDownloader('https://raw.githubusercontent.com/Hemant-Chowdhury/public_files/master/Test.txt')
        self.download_and_match_hash(urlFileDownloader, b"}\xd9\x1e\x07\xf04\x16F\xd5?i8'\x8aM>\x87\x96\x1f\xab\xea\x06o~o@\xb79\x8f;\x0b\x0f")

    def test_large_txt_file_download(self):
        urlFileDownloader = UrlFileDownloader('https://raw.githubusercontent.com/Hemant-Chowdhury/public_files/master/10MB.txt')
        self.download_and_match_hash(urlFileDownloader, b'\xca\x06i\x91X)\xf7w\xb4g5\xe8\xab\xcb\x16\xe2\xc7"Q\x1c\xc8\x9aC\xd4\x02Wzqc\xab\x93l')

    def test_txt_file_download_having_http_scheme(self):
        urlFileDownloader = UrlFileDownloader('http://data.pr4e.org/romeo.txt')
        self.download_and_match_hash(urlFileDownloader, b'\x92Va\xfbF\x8d\xa9P\x82\x8fD\xe4\xc3|\xde\x02K\xaa\xf8M\xb5\xa3\x15E^\xa8\xec\xb94\x8b\x12\xcf')

    def test_pdf_download(self):
        urlFileDownloader = UrlFileDownloader('http://www.africau.edu/images/default/sample.pdf')
        self.download_and_match_hash(urlFileDownloader, b'\x8d\xec\xc8W\x19F\xd4\xcdp\xa0$\x94\x9e\x03:**T7\x7f\xe9\xf1\xc1\xb9D\xc2\x0f\x9e\xe1\x1a\x9eQ')

    def test_image_download_having_different_filename_in_content_disposition(self):
        urlFileDownloader = UrlFileDownloader('https://i.picsum.photos/id/145/200/300.jpg')
        self.download_and_match_hash(urlFileDownloader, b'\xa4\x9b{\xd1J\x13\xc1HlR-\x9c\xa6\xed\x02\x9e;\x93\xa6\xcbp\xb2[\x9dV\x14\xe2\xf6|\x11\x8d\x96')

    def test_video_download(self):
        urlFileDownloader = UrlFileDownloader('https://file-examples.com/wp-content/uploads/2018/04/file_example_MOV_480_700kB.mov')
        self.download_and_match_hash(urlFileDownloader, b'\x867\xa4G\xa9U\x13?w`\x11\xe9\x06\xf1m\xb3uc\x1c\x9b\xd6\xba;\xbc$\xc0\xcf\x03|o\xab\x07')

    def test_invalid_url_having_no_file(self):
        urlFileDownloader = UrlFileDownloader('https://www.google.com')
        with self.assertRaises(InvalidUrl) as context:
            urlFileDownloader.download()
            self.assertEqual(str(context.exception), 'valid file/filename not found')

    def test_invalid_url_having_no_url_scheme(self):
        with self.assertRaises(InvalidUrl) as context:
            UrlFileDownloader('data.pr4e.org/romeo.txt')
            self.assertEqual(str(context.exception), 'url scheme is missing in data.pr4e.org/romeo.txt')

    def test_invalid_url_unreachable(self):
        urlFileDownloader = UrlFileDownloader('http://www.google.com/text/romeo.txt')
        with self.assertRaises(InvalidUrl) as context:
            urlFileDownloader.download()
            self.assertEqual(str(context.exception), 'url not reachable')


if __name__ == '__main__':
    unittest.main()
