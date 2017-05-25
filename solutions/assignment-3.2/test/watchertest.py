import os
import shutil
import tempfile
import unittest

from contextlib import contextmanager
from watcher import Watcher

PATHS_TO_WATCH = '*.txt'


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
        action_to_execute = 'echo > output1.txt'
        path_watcher = Watcher(PATHS_TO_WATCH, action_to_execute)
        open('file1.txt', 'w')
        path_watcher.run_watcher()
        self.assertTrue(os.path.exists('output1.txt'))

    def test_deletingpath(self):
        action_to_execute = 'echo > output2.txt'
        open('file2.txt', 'w')
        path_watcher = Watcher(PATHS_TO_WATCH, action_to_execute)
        os.remove('file2.txt')
        path_watcher.run_watcher()
        self.assertTrue(os.path.exists('output2.txt'))

    def test_updatingpath(self):
        action_to_execute = 'echo > output3.txt'
        open('file3.txt', 'w')
        path_watcher = Watcher(PATHS_TO_WATCH, action_to_execute)
        current_modified_time = os.path.getmtime('file3.txt')
        os.utime(
            'file3.txt',
            (current_modified_time + 1, current_modified_time + 1)
        )
        path_watcher.run_watcher()
        self.assertTrue(os.path.exists('output3.txt'))

    def test_no_path_to_watch_updated(self):
        action_to_execute = 'echo > output4.txt'
        open('file4.txt', 'w')
        path_watcher = Watcher(PATHS_TO_WATCH, action_to_execute)
        open('file5', 'w')
        path_watcher.run_watcher()
        self.assertFalse(os.path.exists('output4.txt'))


if __name__ == '__main__':
    with temporary_directory():
        unittest.main()
