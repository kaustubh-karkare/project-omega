from os import stat
from typing import List, Callable, Dict
from Builder.global_constants import GlobalConstants
from time import sleep


class FileWatcher:
    FILE_WATCH_INTERVAL_SECONDS = GlobalConstants.FILE_WATCH_INTERVAL_SECONDS

    @staticmethod
    def _get_file_edit_times(file_list: List[str]) -> Dict[str, int]:
        """Populate a Dict of last edit times of files and return it"""
        file_edit_times = {}
        for file_path in file_list:
            file_edit_times[file_path] = stat(file_path).st_mtime
        return file_edit_times

    @staticmethod
    def watch_and_execute(file_list: List[str], function: Callable[[any], any], *args: any) -> None:
        """Execute a function whenever a file from file_list changes"""
        print("Listening for changes on {}...".format(file_list))
        file_edit_times = FileWatcher._get_file_edit_times(file_list)
        print("Executing for the first time...")
        function(*args)
        while True:
            sleep(FileWatcher.FILE_WATCH_INTERVAL_SECONDS)
            new_file_edit_times = FileWatcher._get_file_edit_times(file_list)
            if new_file_edit_times != file_edit_times:
                file_edit_times = new_file_edit_times
                print("Detected change of file. Executing...")
                function(*args)


