"""
assumed build rule file template:-
[
    {
        "name": "rule_1",
        "deps": ["current_directory/rule_1_dep_file1", "current_directory/rule_1_dep_file2"],
        "command': 'cat rule_1"
    },
    {
        "name": "rule_2",
        "files": ["rule_2.cpp"],
        "command": "g++ -c rule_2.cpp"
    }
]
"""

import sys
import os
import json
import time

class Builder(object):
    """
    class encapsulation for build tool
    """

    def __init__(self):
        self.output = list()
        self.addr_log = dict()
        self.dir_struct = self.__generate_dir_struct(os.getcwd())
        if len(sys.argv) > 1:
            self.rule = sys.argv[1]
            self.watch_run = bool((len(sys.argv) > 2) and (sys.argv[2] == "--watch"))
            self.rule_exe(self.rule, os.getcwd())
            if self.watch_run:
                self.watch_feature(os.getcwd())


    def rule_exe(self, rule, addr):
        """
        function to execute rule commands and of its dependencies recursively
        """

        self.addr_log[rule] = addr
        os.chdir(addr)

        try:
            build_file = open('build.json', 'r')
        except FileNotFoundError:
            print("Error: Build json file not found!")
            return None
        build_data = json.load(build_file)

        for obj in build_data:
            if obj["name"] == rule:
                if "deps" in obj:
                    for dep in obj["deps"]:
                        if '/' in dep:
                            dep_addr = os.getcwd() + '/' + dep.split('/')[0]
                            dep_rule = dep.split('/')[-1]
                        else:
                            dep_addr = addr
                            dep_rule = dep

                        self.rule_exe(dep_rule, dep_addr)
                        os.chdir(self.addr_log[rule])

                output_file = os.popen(obj["command"])
                output_data = output_file.read()
                if output_data:
                    print(output_data)
                self.output.append(output_data)
                output_file.close()
        build_file.close()
        return self.output

    def watch_feature(self, addr):
        """
        function to implement watch feature which recompiles recently modified files
        """
        while True:
            os.chdir(addr)
            temp_struct = self.__generate_dir_struct(os.getcwd())
            time.sleep(10)
            for file_name in temp_struct:
                try:
                    if temp_struct[file_name] != self.dir_struct[file_name]:
                        self.dir_struct[file_name] = temp_struct[file_name]
                        rule = self.check_parent_rule(file_name, addr)
                        if rule:
                            print(file_name, "changed,", rule, "-rule executing...")
                            self.rule_exe(rule, self.addr_log[rule])
                except KeyError:
                    pass

    @staticmethod
    def check_parent_rule(file_name, base_addr):
        """
        static method that checks the parent of a rule if it is a dependency
        """
        for walk in os.walk(base_addr):
            os.chdir(base_addr)
            os.chdir(walk[0])
            try:
                build_file = open('build.json', 'r')
            except FileNotFoundError:
                continue
            build_data = json.load(build_file)
            for obj in build_data:
                if "deps" in obj:
                    for dep in obj["deps"]:
                        if file_name.split('.')[0] in dep: #weak statement, needs better file checking method
                            os.chdir(base_addr)
                            build_file.close()
                            return obj["name"]

            for obj in build_data:
                if "files" in obj:
                    if file_name in obj["files"]:
                        os.chdir(base_addr)
                        build_file.close()
                        return obj["name"]
            build_file.close()
            return None

    @staticmethod
    def __generate_dir_struct(path):
        """
        generates a dictionary of file name(key) and timestamp of last modification(value)
        """
        base_addr = os.getcwd()
        dir_struct = dict()
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if "pyc" in file_name: #weak statement, needs better method to add only those files required in the build rule file
                    continue
                os.chdir(root)
                dir_struct[file_name] = os.stat(file_name).st_mtime
                os.chdir(base_addr)
        return dir_struct


if __name__ == '__main__':
    tool = Builder()
