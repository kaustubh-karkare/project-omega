import glob
import os
import tempfile
import time
import unittest

from calendar import timegm
from watcher import Watcher

DIRECTORY = tempfile.mkdtemp(dir='/tmp/')
WATCH = DIRECTORY + "/*.cpp"
ACTION = "g++ -o " + DIRECTORY + "/output.o " + DIRECTORY + "/*.cpp"
FILECOUNT = 0


def create_cppfile():
    global FILECOUNT
    FILECOUNT = FILECOUNT + 1
    temp_file = tempfile.NamedTemporaryFile(dir=DIRECTORY, delete=False)
    new_file_name = \
        os.path.join(DIRECTORY, 'testfile' + str(FILECOUNT) + '.cpp')
    old_file_name = os.path.join(DIRECTORY, temp_file.name)
    os.rename(old_file_name, new_file_name)
    return new_file_name


class TestWatcher(unittest.TestCase):

    def test_creatingfile(self):
        path_watcher = \
            Watcher(WATCH, ACTION)
        output_path = os.path.join(DIRECTORY, 'output.o')
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except IOError:
            pass
        previous_block = {}
        for element in glob.glob(WATCH):
            previous_block[element] = os.path.getmtime(element)
        temp_file = create_cppfile()
        path_watcher.start_watcher(previous_block)
        self.assertTrue(os.path.exists(output_path))
        os.remove(os.path.join(DIRECTORY, temp_file))

    def test_updatingfile(self):

        path_watcher = \
            Watcher(WATCH, ACTION)
        temp_file = create_cppfile()
        output_path = os.path.join(DIRECTORY, 'output.o')
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except IOError:
            pass
        previous_block = {}
        for element in glob.glob(WATCH):
            previous_block[element] = os.path.getmtime(element)
        current_time = timegm(time.gmtime())
        os.utime(
            os.path.join(DIRECTORY, temp_file),
            (current_time, current_time)
        )
        path_watcher.start_watcher(previous_block)
        self.assertTrue(os.path.exists(output_path))
        os.remove(os.path.join(DIRECTORY, temp_file))

    def test_deletingfile(self):

        path_watcher = \
            Watcher(WATCH, ACTION)
        temp_file = create_cppfile()
        output_path = os.path.join(DIRECTORY, 'output.o')
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except IOError:
            pass
        previous_block = {}
        for element in glob.glob(WATCH):
            previous_block[element] = os.path.getmtime(element)
        os.remove(os.path.join(DIRECTORY, temp_file))
        path_watcher.start_watcher(previous_block)
        self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    unittest.main()
