import subprocess
import os
import sys
import json
import time

class Builder(object):
    '''
    main class dealing with building
    '''

    def __init__(self):
        self.graph_dict = dict()
        self.graph_loc = {"base_addr" : os.getcwd()}
        self.file_deps = dict()
        self.file_watch = dict()

    def serial_exe(self, rule, resolved=[], unresolved=[]):
        '''
        executes rules and their dependencies serially
        '''
        unresolved.append(rule)
        rule_obj = self.graph_dict[rule]
        for dep in rule_obj.unresolved_deps:
            if dep not in resolved:
                if dep in unresolved:
                    raise Exception("Circular dependency detected!")
                self.serial_exe(dep, resolved, unresolved)
        if rule_obj.command:
            subprocess.run((rule_obj.command), cwd=self.graph_loc[rule], shell=True)
        resolved.append(rule)
        unresolved.remove(rule)

    def create_graph(self):
        '''
        links rules and their dependencies forming a graph from a rule json file
        '''
        for root, dirs, files in os.walk(os.getcwd()):
            if 'build.json' in files:
                with open(root + '/build.json') as build_file:
                    rule_json = json.load(build_file)
                    for obj in rule_json:
                        rule_name = root.partition(self.graph_loc["base_addr"])[-1][1:] + "/" + obj["name"] if root != self.graph_loc["base_addr"] else obj["name"]
                        if rule_name not in self.graph_dict:
                            self.graph_dict[rule_name] = Rule(obj["name"])
                        self.graph_loc[rule_name] = root
                        if "deps" in obj:
                            for dep in obj["deps"]:
                                self.graph_dict[rule_name].addDeps(dep)
                                if dep not in self.graph_dict:
                                    self.graph_dict[dep] = Rule(dep)
                                self.graph_dict[dep].parents.append(rule_name)
                        if "command" in obj:
                            self.graph_dict[rule_name].command = obj["command"]

    def map_file_command(self, rule):
        if rule in self.file_deps.values():
            return
        files = input("Enter depended files for %s(Press Enter if none): " % (rule)).split()
        for file in files:
            self.file_deps[file] = rule
        for dep in self.graph_dict[rule].unresolved_deps:
            self.map_file_command(dep)


    def parallel_exe(self, rule):
        '''
        executes rules and their dependencies in parallel reducing execution time
        '''
        process_to_execute = self.get_independent_deps(rule)
        name_to_process = {dep: subprocess.Popen((self.graph_dict[dep].command), cwd=self.graph_loc[dep], shell=True) for dep in process_to_execute if self.graph_dict[dep].command}
        while True:
            for dep in list(name_to_process):
                if name_to_process[dep].poll() is None:
                    continue
                else:
                    dep_obj = self.graph_dict[dep]
                    del name_to_process[dep]
                    process_to_execute.remove(dep)
                    for parent in dep_obj.parents:
                        self.graph_dict[parent].remDeps(dep)
                        if not self.graph_dict[parent].unresolved_deps:
                            process_to_execute.add(parent)
                            if self.graph_dict[parent].command:
                                name_to_process[parent] = subprocess.Popen((self.graph_dict[parent].command), cwd=self.graph_loc[parent], shell=True)

            if not name_to_process:
                break
            time.sleep(1)

    def get_independent_deps(self, rule):
        '''
        returns a set of independent dependencies to form the base of parallel execution
        '''
        visited, stack = set(), [rule]
        independent_deps = set()
        visited.add(rule)
        while stack:
            vertex  =  stack.pop()
            for dep in self.graph_dict[vertex].unresolved_deps:
                if dep not in visited:
                    stack.append(dep)
                    if not self.graph_dict[dep].unresolved_deps:
                        independent_deps.add(dep)
                    visited.add(dep)
        return independent_deps


    def watch_changes(self):
        if not self.file_deps: return
        while True:
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    if file in self.file_deps:
                        if file in self.file_watch:
                            if self.file_watch[file] != os.stat(root+'/'+file).st_mtime:
                                self.serial_exe(self.file_deps[file], [], [])
                                for parent in self.graph_dict[self.file_deps[file]].parents:
                                    self.serial_exe(parent, [], [])
                                self.file_watch[file] = os.stat(root+'/'+file).st_mtime
                        else:                            
                            self.file_watch[file] = os.stat(root+'/'+file).st_mtime
            time.sleep(1)

class Rule(object):

    def __init__(self, name):
        self.name = name
        self.resolved_deps = list()
        self.unresolved_deps = list()
        self.parents = list()
        self.command = None

    def addDeps(self, dep):
        self.unresolved_deps.append(dep)

    def remDeps(self, dep):
        self.unresolved_deps.remove(dep)
        self.resolved_deps.append(dep)
