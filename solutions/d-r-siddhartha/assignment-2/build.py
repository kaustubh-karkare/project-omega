import subprocess
import os
import json
import time

class Graph():

    def __init__(self):
        self.BASE_ADDR = os.getcwd()
        self.rule_name_to_rule = dict()
        self.RULE_FILE = 'build.json'

    def create_graph(self):
        '''
        links rules and their dependencies forming a graph from a rule json file
        '''
        for root, _, files in os.walk(self.BASE_ADDR):
            if self.RULE_FILE in files:
                with open(os.path.join(root, self.RULE_FILE)) as build_file:
                    rule_json = json.load(build_file)
                    for obj in rule_json:
                        rule_name = self.generate_rule_name(root, obj["name"])
                        if rule_name not in self.rule_name_to_rule:
                            self.rule_name_to_rule[rule_name] = Rule(obj["name"])
                        self.rule_name_to_rule[rule_name].create(obj, rule_name, self.rule_name_to_rule, root)

    def generate_rule_name(self, addr, rule):
        '''generates the name of the rule with a relative path'''

        if addr != self.BASE_ADDR:
            name = os.path.join(addr.partition(self.BASE_ADDR)[-1][1:], rule)
        else:
            name = rule
        return name

    def detect_circular_dependency(self, rule, resolved=[], seen=[]):
        seen.append(rule)
        rule_obj = self.rule_name_to_rule[rule]
        for dep in rule_obj.deps:
            if dep not in resolved:
                if dep in seen:
                    raise Exception("Circular dependency detected!")
                self.detect_circular_dependency(dep, resolved, seen)
        resolved.append(rule)
        return False


class ParallelExe():

    def __init__(self, graph):
        self.graph = graph
        self.unresolved_deps = {rule: self.graph[rule].deps for rule in self.graph}
        self.resolved_deps = {rule: list() for rule in self.graph}

    def exe(self, rule):
        '''
        executes rules and their dependencies in parallel reducing execution time
        '''
        process_to_execute = self.get_independent_deps(rule)
        name_to_process = {dep: self.graph[dep].exe_rule() for dep in process_to_execute}
        while True:
            for dep in list(name_to_process):
                if name_to_process[dep].poll() is None:
                    continue
                else:
                    dep_obj = self.graph[dep]
                    del name_to_process[dep]
                    process_to_execute.remove(dep)
                    for parent in dep_obj.parents:
                        self.unresolved_deps[parent].remove(dep)
                        self.resolved_deps[parent].append(dep)
                        if not self.unresolved_deps[parent]:
                            process_to_execute.add(parent)
                            if self.graph[parent].command:
                                name_to_process[parent] = self.graph[parent].exe_rule()

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
            vertex = stack.pop()
            for dep in self.graph[vertex].deps:
                if dep not in visited:
                    stack.append(dep)
                    if not self.graph[dep].deps:
                        independent_deps.add(dep)
                    visited.add(dep)
        return independent_deps


class SerialExe():

    def __init__(self, graph):
        self.graph = graph

    def exe(self, rule, resolved=[], unresolved=[]):
        '''
        executes rules and their dependencies serially
        '''
        unresolved.append(rule)
        rule_obj = self.graph[rule]
        for dep in rule_obj.deps:
            if dep not in resolved:
                self.exe(dep, resolved, unresolved)
        process = rule_obj.exe_rule()
        if process:
            process.wait()
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
            for root, _, files in os.walk(os.getcwd()): #base addr inaccesible from graph as the dictionary is being taken instead of the whole object, thus os.getcwd is used again
                for file in set(self.file_deps).intersection(set(files)):
                    file_edit_time = os.stat(os.path.join(root, file)).st_mtime
                    if file in self.file_watch:
                        if self.file_watch[file] < file_edit_time:
                            print(file, "changed...")
                            print("recompiling files...")
                            self.executor.exe(self.file_deps[file])
                            for parent in self.executor.graph[self.file_deps[file]].parents:
                                self.executor.exe(parent)
                            self.file_watch[file] = file_edit_time
                    else:
                        self.file_watch[file] = file_edit_time
            time.sleep(1)

    def map_file_command(self, rule):
        '''maps files to commands to assist in implementing the watch feature'''
        if rule in self.file_deps.values():
            return
        files = input("Enter depended files for %s(Press Enter if none): " % (rule)).split()
        for file in files:
            self.file_deps[file] = rule
        for dep in self.executor.graph[rule].deps:
            self.map_file_command(dep)


class Rule():

    def __init__(self, name):
        self.name = name
        self.deps = list()
        self.parents = list()
        self.command = None
        self.address = None

    def addDeps(self, dep):
        self.deps.append(dep)

    def remDeps(self, dep):
        self.deps.remove(dep)

    def exe_rule(self):
        if self.command:
            return subprocess.Popen((self.command), cwd=self.address, shell=True)
        else:
            return None

    def create(self, obj, rule_name, rule_name_to_rule, addr):
        if "deps" in obj:
            for dep in obj["deps"]:
                rule_name_to_rule[rule_name].addDeps(dep)
                if dep not in rule_name_to_rule:
                    rule_name_to_rule[dep] = Rule(dep)
                rule_name_to_rule[dep].parents.append(rule_name)
        if "command" in obj:
            rule_name_to_rule[rule_name].command = obj["command"]
        self.address = addr
