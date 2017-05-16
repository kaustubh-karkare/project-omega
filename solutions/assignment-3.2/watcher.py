import os
import logging
import subprocess
import time

from glob import glob
from threading import Thread


class Watcher(Thread):

    def __init__(
            self,
            paths_to_watch,
            action_to_execute,
            interval_between_checks=1
    ):
        logging.info('Logger for  Watcher')
        self.logger = \
            logging.getLogger(paths_to_watch + ' : ' + action_to_execute)
        self.paths_to_watch = paths_to_watch
        self.action_to_execute = action_to_execute
        self.interval_between_checks = interval_between_checks
        self.watching = False
        Thread.__init__(self)

    def run(self):
        previous_paths = {}
        for element in glob(self.paths_to_watch):
            try:
                previous_paths[element] = os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')
        self.watching = True
        while self.watching:
            self.start_watcher(previous_paths)
            time.sleep(self.interval_between_checks)

    def start_watcher(self, previous_paths):
        current_paths = {}
        for element in glob(self.paths_to_watch):
            try:
                current_paths[element] = os.path.getmtime(element)
            except IOError:
                self.logger.info('Path - ' + element + 'Not Available')
        if set(previous_paths.items()) != set(current_paths.items()):
            self.logger.info('Executing requested action')
            subprocess.call(self.action_to_execute, shell=True)
        previous_paths.clear()
        previous_paths.update(current_paths)

    def stop_watcher(self):
        self.watching = False
