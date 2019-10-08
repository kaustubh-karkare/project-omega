import unittest
from Builder.lib.file_watcher import FileWatcher
import os
from time import sleep
from multiprocessing import Process
import tempfile


def copy_file(input_file_path: str, output_file_path: str) -> None:
    with open(input_file_path, 'r') as file:
        contents = file.read()
    with open(output_file_path, 'w') as file:
        file.write(contents)


class TestFileWatcher(unittest.TestCase):
    def test_copy_file_on_file_change(self):
        with tempfile.TemporaryDirectory() as file_path:
            input_file = file_path + "/input.txt"
            output_file = file_path + "/output.txt"
            with open(input_file, 'w') as file_handle:
                file_handle.write("Hello World 1.0")
            with open(output_file, 'w') as file_handle:
                file_handle.write("Hello World 1.0")

            # Activate Watcher and change tracked file
            file_watcher = FileWatcher()
            process = Process(target=file_watcher.watch_and_execute,
                              args=([input_file], copy_file, input_file, output_file))
            process.start()
            with open(input_file, 'w') as file_handle:
                file_handle.write("Hello World 2.0")
            sleep(2)
            with open(output_file, 'r') as file_handle:
                output_file_content = file_handle.read()
            self.assertEqual("Hello World 2.0", output_file_content)

            # Cleanup
            with open(input_file, 'w') as file_handle:
                file_handle.write("Hello World 1.0")
            os.remove(output_file)
            process.terminate()


if __name__ == '__main__':
    unittest.main()
