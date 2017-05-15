import os
import unittest
import time

from calendar import timegm
from tempfile import NamedTemporaryFile
from buildutility import BuildUtility

WATCH = "/tmp/test/*.cpp"
ACTION = "g++ -o /tmp/test/final.exe /tmp/test/*.cpp"


class TestBuildUtility(unittest.TestCase):

    def test_build_files(self):
        build_instance = \
            BuildUtility(WATCH, ACTION)
        output_file = '/tmp/test/final.exe'
        try:
            os.remove(output_file)
        except OSError:
            pass
        self.assertFalse(os.path.exists(output_file))
        build_instance.build_files()
        self.assertTrue(os.path.exists(output_file))
        build_instance.stop_buildutility()

    def test_creatingfile(self):
        build_instance = \
            BuildUtility(WATCH, ACTION)
        directory = os.path.dirname(WATCH)
        build_instance.start()
        time.sleep(.5)
        self.assertTrue(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        _ = NamedTemporaryFile(dir=directory)
        time.sleep(1)
        self.assertFalse(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        build_instance.stop_buildutility()

    def test_updatingfile(self):

        build_instance = \
            BuildUtility(WATCH, ACTION)
        directory = os.path.dirname(WATCH)
        build_instance.start()
        time.sleep(.5)
        self.assertTrue(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        current_time = timegm(time.gmtime())
        os.utime(
            os.path.join(directory, 'testfile.cpp'),
            (current_time, current_time)
        )
        time.sleep(1)
        self.assertFalse(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        build_instance.stop_buildutility()

    def test_deletingfile(self):
        build_instance = \
            BuildUtility(WATCH, ACTION)
        directory = os.path.dirname(WATCH)
        temp_file = NamedTemporaryFile(dir=directory, delete=False)
        temp_file.close()
        build_instance.start()
        time.sleep(.5)
        self.assertTrue(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        os.remove(os.path.join(directory, temp_file.name))
        time.sleep(1)
        self.assertFalse(build_instance.path_thread_is_alive)
        self.assertTrue(build_instance.buildutility_is_alive)
        build_instance.stop_buildutility()


if __name__ == '__main__':
    unittest.main()
