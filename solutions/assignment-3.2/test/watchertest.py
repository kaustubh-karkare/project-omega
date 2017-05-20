import os
import tempfile
import unittest

from watcher import Watcher

DIRECTORY = tempfile.mkdtemp(dir='/tmp/')
OUTPUT_PATH = tempfile.mkstemp(dir=DIRECTORY)
PATHS_TO_WATCH = DIRECTORY
ACTION_TO_EXECUTE = "echo True> " + OUTPUT_PATH[1]


class TestWatcher(unittest.TestCase):

    def test_creatingpath(self):
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        with tempfile.TemporaryFile(dir=DIRECTORY) as _:
            path_watcher.run_watcher()
        with open(OUTPUT_PATH[1], 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_deletingpath(self):
        temp_file = tempfile.mkstemp(dir=DIRECTORY)
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        os.remove(os.path.join(DIRECTORY, temp_file[1]))
        path_watcher.run_watcher()
        with open(OUTPUT_PATH[1], 'r') as output:
            self.assertEqual(output.read(), "True\n")

    def test_updatingpath(self):
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        current_modified_time = os.path.getmtime(DIRECTORY)
        os.utime(
            DIRECTORY,
            (current_modified_time + 1, current_modified_time + 1)
        )
        path_watcher.run_watcher()
        with open(OUTPUT_PATH[1], 'r') as output:
            self.assertEqual(output.read(), 'True\n')

    def test_updatefile_within_path(self):
        temp_file = tempfile.mkstemp(dir=DIRECTORY)
        path_watcher = Watcher(PATHS_TO_WATCH, ACTION_TO_EXECUTE)
        current_modified_time = os.path.getmtime(temp_file[1])
        os.utime(
            temp_file[1],
            (current_modified_time + 1, current_modified_time + 1)
        )
        with open(OUTPUT_PATH[1], 'w+') as output:
            path_watcher.run_watcher()
            self.assertNotEqual(output.read(), 'True\n')

if __name__ == '__main__':
    unittest.main()
