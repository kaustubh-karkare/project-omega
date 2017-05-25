import logging
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
        logger=logging.getLogger('Watcher'),
        interval_between_checks=1,
    ):
        self.paths_to_watch = paths_to_watch
        self.action_to_execute = action_to_execute
        self.logger = logger
        self.interval_between_checks = interval_between_checks
        self.watching = False
        self.previous_modified_times = {}
        for element in glob(self.paths_to_watch):
            try:
                self.previous_modified_times[element] = \
                    os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')

        Thread.__init__(self)

    def run(self):
        self.watching = True
        while self.watching:
            self.run_watcher()
            time.sleep(self.interval_between_checks)

    def run_watcher(self):
        current_modified_times = {}
        for element in glob(self.paths_to_watch):
            try:
                current_modified_times[element] = os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')

        should_execute_action = False
        # Check if new path is added or updated.
        for current_path, current_time in current_modified_times.items():
            if current_path in self.previous_modified_times:
                if current_time > self.previous_modified_times[current_path]:
                    should_execute_action = True
                    break
                else:
                    del self.previous_modified_times[current_path]
            else:
                should_execute_action = True
                break

        # Check if any previous path is deleted.
        if not should_execute_action:
            if self.previous_modified_times:
                should_execute_action = True

        if should_execute_action:
            subprocess.call(self.action_to_execute, shell=True)
        self.previous_modified_times = current_modified_times

    def stop_watcher(self):
        self.watching = False
