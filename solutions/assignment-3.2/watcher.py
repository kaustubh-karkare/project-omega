import os
import subprocess
import time

from glob import glob
from threading import Thread


class Watcher(Thread):

    def __init__(
        self,
        paths_to_watch,
        action_to_execute,
        logger,
        interval_between_checks=1,
    ):
        self.paths_to_watch = paths_to_watch
        self.action_to_execute = action_to_execute
        self.interval_between_checks = interval_between_checks
        self.watching = False
        self.logger = logger
        Thread.__init__(self)

    def run(self):
        previous_modified_time = {}
        for element in glob(self.paths_to_watch):
            try:
                previous_modified_time[element] = os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')
        self.watching = True
        while self.watching:
            self.run_watcher(previous_modified_time)
            time.sleep(self.interval_between_checks)

    def run_watcher(self, previous_modified_time):
        current_modified_time = {}
        for element in glob(self.paths_to_watch):
            try:
                current_modified_time[element] = os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')
        action_executed = False
        # Check if new path is added or updated.
        for current_path, current_time in current_modified_time.items():
            if current_path in previous_modified_time:
                if current_time - previous_modified_time[current_path] > 0:
                    action_executed = True
                    subprocess.call(self.action_to_execute, shell=True)
                    break
                else:
                    del previous_modified_time[current_path]
            else:
                action_executed = True
                subprocess.call(self.action_to_execute, shell=True)
                break
        # Check if any previous path is deleted.
        if not action_executed:
            if previous_modified_time:
                subprocess.call(self.action_to_execute, shell=True)
        previous_modified_time.clear()
        previous_modified_time.update(current_modified_time)

    def stop_watcher(self):
        self.watching = False
