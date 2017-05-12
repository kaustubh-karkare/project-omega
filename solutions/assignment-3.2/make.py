import json
import logging
import os
import subprocess
import threading


class Make(threading.Thread):

    def __init__(self, path):
        self.path = path
        self.utility_to_run = False
        threading.Thread.__init__(self)

    def run(self):
        self.start_utility()

    def start_utility(self):
        descriptor_stored_timestamp = os.path.getmtime(self.path)
        threading.Thread(
            target=self.run_utility,
            args=()
        ).start()
        threading.Thread(
            target=self.restart_utility,
            args=(descriptor_stored_timestamp,)
        ).start()

    def validate_and_update_target(self, target, descriptor_list):
        target_element = None
        for element in descriptor_list:
            if element['target'] is target:
                target_element = element
                break
        if target_element is None:
            return
        dependency_list = target_element['dependency']
        command_list = target_element['command']
        target_path = os.path.join(os.path.dirname(self.path), target)
        execute_commands = False
        if os.path.isfile(target_path):
            target_modified_timestamp = os.path.getmtime(target_path)
        else:
            target_modified_timestamp = 0
            execute_commands = True
        for element in dependency_list:
            self.validate_and_update_target(element, descriptor_list)
            element_path = os.path.join(os.path.dirname(self.path), element)
            try:
                element_modified_timestamp = \
                    os.path.getmtime(element_path)
            except os.error:
                logging.error('Dependecy missing')
                raise
            if element_modified_timestamp - target_modified_timestamp > 0:
                execute_commands = True
        if execute_commands:
            for command in command_list:
                subprocess.call(command, shell=True)

    def run_utility(self):
        self.utility_to_run = True
        with open(self.path, 'r') as descriptor_file:
            descriptor_list = json.load(descriptor_file)
        while self.utility_to_run:
            for element in descriptor_list:
                self.validate_and_update_target(
                    element['target'],
                    descriptor_list
                )

    def stop_utility(self):
        self.utility_to_run = False

    def restart_utility(self, descriptor_stored_timestamp):
        while self.utility_to_run:
            descriptor_current_timestamp = \
                os.path.getmtime(self.path)
            if descriptor_current_timestamp - descriptor_stored_timestamp > 0:
                descriptor_stored_timestamp = descriptor_current_timestamp
                self.stop_utility()
                self.start_utility()

