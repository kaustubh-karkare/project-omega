from os import stat
from typing import List, Callable, Dict
from time import sleep


class FileWatcher:
    FILE_WATCH_INTERVAL_SECONDS = 1

    def _get_file_edit_times(self, file_list: List[str]) -> Dict[str, int]:
        """Populate a Dict of last edit times of files and return it"""
        file_edit_times = {}
        for file in file_list:
            file_edit_times[file] = stat(file).st_mtime
        return file_edit_times

    def watch_and_execute(self, file_list: List[str], function: Callable[[any], any], *args: any) -> None:
        """Execute a function whenever a file from file_list changes"""
        print("Listening for changes on {}...".format(file_list))
        file_edit_times = self._get_file_edit_times(file_list)
        print("Executing command for the first time...")
        function(*args)
        while True:
            sleep(FileWatcher.FILE_WATCH_INTERVAL_SECONDS)
            new_file_edit_times = self._get_file_edit_times(file_list)
            if new_file_edit_times != file_edit_times:
                file_edit_times = new_file_edit_times
                print("Detected change of file. Executing command...")
                function(*args)


