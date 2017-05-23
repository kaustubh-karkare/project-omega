import os
import shutil
import tempfile
import time
import unittest

from watcher import Watcher


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
        for testing_path in temporary_directory():
            output_path = 'out.txt'
            paths_to_watch = testing_path
            action_to_execute = "echo True> " + output_path
            path_watcher = Watcher(paths_to_watch, action_to_execute)
            time.sleep(0.1)
            with tempfile.TemporaryFile(dir=testing_path) as _:
                path_watcher.run_watcher()
            with open(output_path, 'r') as output:
                self.assertEqual(output.read(), "True\n")

    def test_deletingpath(self):
        for testing_path in temporary_directory():
            temp_file = \
                tempfile.NamedTemporaryFile(dir=testing_path, delete=False)
            output_path = 'out.txt'
            paths_to_watch = testing_path
            action_to_execute = "echo True> " + output_path
            path_watcher = Watcher(paths_to_watch, action_to_execute)
            time.sleep(0.1)
            os.remove(temp_file.name)
            path_watcher.run_watcher()
            with open(output_path, 'r') as output:
                self.assertEqual(output.read(), "True\n")

    def test_updatingpath(self):
        for testing_path in temporary_directory():
            output_path = 'out.txt'
            paths_to_watch = testing_path
            action_to_execute = "echo True> " + output_path
            path_watcher = Watcher(paths_to_watch, action_to_execute)
            current_modified_time = os.path.getmtime(testing_path)
            os.utime(
                testing_path,
                (current_modified_time + 1, current_modified_time + 1)
            )
            path_watcher.run_watcher()
            with open(output_path, 'r') as output:
                self.assertEqual(output.read(), 'True\n')

    def test_updatefile_within_path(self):
        for testing_path in temporary_directory():
            output_path = 'out.txt'
            paths_to_watch = testing_path
            action_to_execute = "echo True> " + output_path
            temp_file = \
                tempfile.NamedTemporaryFile(dir=testing_path, delete=False)
            path_watcher = Watcher(paths_to_watch, action_to_execute)
            current_modified_time = os.path.getmtime(temp_file.name)
            os.utime(
                temp_file.name,
                (current_modified_time + 1, current_modified_time + 1),
            )
            path_watcher.run_watcher()
            self.assertFalse(os.path.exists(output_path))

if __name__ == '__main__':
    unittest.main()
