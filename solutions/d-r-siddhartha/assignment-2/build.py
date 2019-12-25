import subprocess
import os
import sys
import json
import time

class Graph(object):

    def __init__(self):
        self.graph_loc = {"base_addr" : os.getcwd()}
        self.graph_dict = dict()

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


class ParallelExe(object):

    def __init__(self, graph, location_map):
        self.graph = graph
        self.location_map = location_map

    def exe(self, rule):
        '''
        executes rules and their dependencies in parallel reducing execution time
        '''
        process_to_execute = self.get_independent_deps(rule)
        name_to_process = {dep: subprocess.Popen((self.graph[dep].command), cwd=self.location_map[dep], shell=True) for dep in process_to_execute if self.graph[dep].command}
        while True:
            for dep in list(name_to_process):
                if name_to_process[dep].poll() is None:
                    continue
                else:
                    dep_obj = self.graph[dep]
                    del name_to_process[dep]
                    process_to_execute.remove(dep)
                    for parent in dep_obj.parents:
                        self.graph[parent].remDeps(dep)
                        if not self.graph[parent].unresolved_deps:
                            process_to_execute.add(parent)
                            if self.graph[parent].command:
                                name_to_process[parent] = subprocess.Popen((self.graph[parent].command), cwd=self.location_map[parent], shell=True)

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
            for dep in self.graph[vertex].unresolved_deps:
                if dep not in visited:
                    stack.append(dep)
                    if not self.graph[dep].unresolved_deps:
                        independent_deps.add(dep)
                    visited.add(dep)
        return independent_deps


class SerialExe(object):

    def __init__(self, graph, location_map):
        self.graph = graph
        self.location_map = location_map

    def exe(self, rule, resolved=[], unresolved=[]):
        '''
        executes rules and their dependencies serially
        '''
        unresolved.append(rule)
        rule_obj = self.graph[rule]
        for dep in rule_obj.unresolved_deps:
            if dep not in resolved:
                if dep in unresolved:
                    raise Exception("Circular dependency detected!")
                self.exe(dep, resolved, unresolved)
        if rule_obj.command:
            subprocess.run((rule_obj.command), cwd=self.location_map[rule], shell=True)
        resolved.append(rule)
        unresolved.remove(rule)

class WatchChanges():

    def __init__(self, executor):
        self.executor = executor
        self.file_deps = dict()
        self.file_watch = dict()

    def watch_init(self):
        if not self.file_deps: return
        while True:
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    if file in self.file_deps:
                        if file in self.file_watch:
                            if self.file_watch[file] != os.stat(root+'/'+file).st_mtime:
                                print(file, "changed...")
                                print("recompiling files...")
                                self.executor.exe(self.file_deps[file])
                                for parent in self.executor.graph[self.file_deps[file]].parents:
                                    self.executor.exe(parent)
                                self.file_watch[file] = os.stat(root+'/'+file).st_mtime
                        else:
                            print(root+'/'+file)
                            self.file_watch[file] = os.stat(root+'/'+file).st_mtime
            time.sleep(1)

    def map_file_command(self, rule):
        if rule in self.file_deps.values():
            return
        files = input("Enter depended files for %s(Press Enter if none): " % (rule)).split()
        for file in files:
            self.file_deps[file] = rule
        for dep in self.executor.graph[rule].unresolved_deps:
            self.map_file_command(dep)


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
