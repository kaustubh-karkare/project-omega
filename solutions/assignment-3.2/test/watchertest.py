import os
import shutil
import tempfile
import unittest

from contextlib import contextmanager
from watcher import Watcher

PATHS_TO_WATCH = '*.txt'
ACTION_TO_EXECUTE = 'echo > output1.txt'


@contextmanager
def temporary_directory():
    original_path = os.getcwd()
    testing_path = tempfile.mkdtemp()
    try:
        os.chdir(testing_path)
        yield testing_path
    finally:
        os.chdir(original_path)
        shutil.rmtree(testing_path)


class TestWatcher(unittest.TestCase):

    def test_creatingpath(self):
        with temporary_directory():
            path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
            open('file1.txt', 'w').close()
            path_watcher.run_watcher()
            self.assertTrue(os.path.exists('output1.txt'))

    def test_deletingpath(self):
        with temporary_directory():
            open('file1.txt', 'w').close()
            path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
            os.remove('file1.txt')
            path_watcher.run_watcher()
            self.assertTrue(os.path.exists('output1.txt'))

    def test_updatingpath(self):
        with temporary_directory():
            open('file1.txt', 'w').close()
            path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
            current_modified_time = os.path.getmtime('file1.txt')
            os.utime(
                'file1.txt',
                (current_modified_time + 1, current_modified_time + 1)
            )
            path_watcher.run_watcher()
            self.assertTrue(os.path.exists('output1.txt'))

    def test_no_path_to_watch_updated(self):
        with temporary_directory():
            open('file1.txt', 'w').close()
            path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
            open('file2', 'w').close()
            path_watcher.run_watcher()
            self.assertFalse(os.path.exists('output1.txt'))


if __name__ == '__main__':
    unittest.main()
