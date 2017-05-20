import os
import tempfile
import unittest

from watcher import Watcher

DIRECTORY = tempfile.mkdtemp(dir='/tmp/')
OUTPUT_DIRECTORY = tempfile.mkdtemp(dir='/tmp/')
OUTPUT_PATH = os.path.join(OUTPUT_DIRECTORY, 'out.txt')
WATCH = DIRECTORY
ACTION = "echo True> " + os.path.join(OUTPUT_DIRECTORY, "out.txt")


class TestWatcher(unittest.TestCase):

    def test_creatingpath(self):
        path_watcher = Watcher(WATCH, ACTION)
        with tempfile.TemporaryFile(dir=DIRECTORY) as _:
            path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_deletingpath(self):
        temp_file = tempfile.mkstemp(dir=DIRECTORY)
        path_watcher = Watcher(WATCH, ACTION)
        os.remove(os.path.join(DIRECTORY, temp_file[1]))
        path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_updatingpath(self):
        path_watcher = Watcher(WATCH, ACTION)
        current_modified_time = os.path.getmtime(DIRECTORY)
        os.utime(
            DIRECTORY,
            (current_modified_time + 1, current_modified_time + 1)
        )
        path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), 'True\n')

if __name__ == '__main__':
    unittest.main()
