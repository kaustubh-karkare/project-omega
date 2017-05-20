import os
import tempfile
import unittest

from watcher import Watcher

DIRECTORY = tempfile.mkdtemp(dir='/tmp/')
OUTPUT_PATH = os.path.join(DIRECTORY, 'out.txt')
PATHS_TO_WATCH = DIRECTORY
ACTION_TO_EXECUTE = "echo True> " + OUTPUT_PATH


class TestWatcher(unittest.TestCase):

    def test_creatingpath(self):
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        with tempfile.TemporaryFile(dir=DIRECTORY) as _:
            path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_deletingpath(self):
        temp_file = tempfile.TemporaryFile(dir=DIRECTORY)
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        os.remove(os.path.join(DIRECTORY, temp_file.name))
        path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_updatingpath(self):
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        current_modified_time = os.path.getmtime(DIRECTORY)
        os.utime(
            DIRECTORY,
            (current_modified_time + 1, current_modified_time + 1)
        )
        path_watcher.run_watcher()
        with open(OUTPUT_PATH, 'r') as output:
            self.assertEqual(output.read(), 'True\n')

    def test_updatingfile_within_path(self):
        temp_file = tempfile.mkstemp(dir=DIRECTORY)
        current_modified_time = os.path.getmtime(OUTPUT_PATH)
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        os.utime(
            temp_file[1],
            (current_modified_time + 1, current_modified_time + 1)
        )
        with open(OUTPUT_PATH, 'w+') as output:
            path_watcher.run_watcher()
            self.assertNotEqual(output.read(), 'True\n')

if __name__ == '__main__':
    unittest.main()
