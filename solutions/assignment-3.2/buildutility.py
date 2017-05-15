import os
import logging
import subprocess
import time

from glob import glob
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class BuildUtility(Thread):

    def __init__(self, watch, action):
        logging.info('Logger for  BuildUtility')
        self.logger = \
            logging.getLogger(watch + ' : ' + action)
        self.watch = watch
        self.action = action
        self.buildutility_is_alive = False
        self.path_thread_is_alive = False
        Thread.__init__(self)

    def run(self):
        self.start_buildutility()

    def start_buildutility(self):
        interval_between_checks = 1
        self.buildutility_is_alive = True
        while self.buildutility_is_alive:
            self.path_thread_is_alive = True
            with ThreadPoolExecutor(max_workers=len(glob(self.watch)) + 1) \
                    as executor:
                executor.submit(
                    self.watch_paths_for_updation,
                    os.path.dirname(self.watch),
                    interval_between_checks
                )
                for element in glob(self.watch):
                    executor.submit(
                        self.watch_paths_for_updation,
                        element,
                        interval_between_checks
                    )
            if not self.path_thread_is_alive and self.buildutility_is_alive:
                self.build_files()
            time.sleep(interval_between_checks)

    def watch_paths_for_updation(self, file_path, interval_between_checks):
        try:
            stored_modified_time = os.path.getmtime(file_path)
        except IOError:
            self.logger.warning('Path - ' + file_path + ' Not Available')
            return
        while self.path_thread_is_alive:
            try:
                current_modified_time = os.path.getmtime(file_path)
            except IOError:
                self.logger.warning('Path - ' + file_path + ' Modified')
                self.path_thread_is_alive = False
                break
            if current_modified_time - stored_modified_time > 0:
                self.logger.info('Path - ' + file_path + ' Modified')
                self.path_thread_is_alive = False
                break
            time.sleep(interval_between_checks)

    def build_files(self):
        file_list = ''
        for element in glob(self.watch):
            file_list = file_list + element + ' '
        subprocess.call(
            self.action.replace(self.watch, file_list),
            shell=True
            )

    def stop_buildutility(self):
        self.path_thread_is_alive = False
        self.buildutility_is_alive = False
