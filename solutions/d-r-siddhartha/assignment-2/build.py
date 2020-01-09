import subprocess
import os
import json
import time

class Rule():

    def __init__(self, name):
        self.name = name
        self.dependencies = list()
        self.dependents = list()
        self.command = None
        self.cwd = None
        self.name_with_relative_path = None

    def addDeps(self, dep):
        self.dependencies.append(dep)

    def exe_rule(self):
        if self.command:
            return subprocess.Popen((self.command), cwd=self.cwd, shell=True)
        else:
            return None

    def generate_rule_name(self, base_addr):
        '''generates the name of the rule with a relative path'''

        if self.cwd != base_addr:
            name = os.path.join(self.cwd.partition(base_addr)[-1][1:], self.name)
        else:
            name = self.name
        self.name_with_relative_path = name

    @classmethod
    def create(cls, obj, addr, base_addr):
        rule_obj = cls(obj["name"])
        rule_obj.cwd = addr
        if "deps" in obj:
            for dep in obj["deps"]:
                rule_obj.addDeps(dep)
        if "command" in obj:
            rule_obj.command = obj["command"]
        rule_obj.generate_rule_name(base_addr)
        return rule_obj


class Graph():

    RULE_FILE = 'build.json'

    def __init__(self, base_addr=os.getcwd()):
        self.base_addr = base_addr
        self.rule_name_to_rule = dict()

    def create_graph(self):
        '''
        links rules and their dependencies forming a graph from a rule json file
        '''
        for root, _, files in os.walk(self.base_addr):
            if self.RULE_FILE in files:
                with open(os.path.join(root, self.RULE_FILE)) as build_file:
                    rule_json = json.load(build_file)
                    for obj in rule_json:
                        rule = Rule.create(obj, root, self.base_addr)
                        self.rule_name_to_rule[rule.name_with_relative_path] = rule
        self.add_dependents()

    def add_dependents(self):
        '''adding dependents'''
        for rule_name in self.rule_name_to_rule:
            for dep_name in self.rule_name_to_rule[rule_name].dependencies:
                self.rule_name_to_rule[dep_name].dependents.append(rule_name)


    def detect_circular_dependency(self, rule, resolved=None, seen=None):
        if type(resolved) != list:
            resolved = list()
        if type(seen) != list:
            seen = list()
        seen.append(rule)
        rule_obj = self.rule_name_to_rule[rule]
        for dep in rule_obj.dependencies:
            if dep not in resolved:
                if dep in seen:
                    raise Exception("Circular dependency detected!")
                self.detect_circular_dependency(dep, resolved, seen)
        resolved.append(rule)
        return False



class ParallelExe():

    def __init__(self, graph_obj):
        self.graph_obj = graph_obj
        self.graph = graph_obj.rule_name_to_rule
        self.unresolved_deps = {rule: self.graph[rule].dependencies for rule in self.graph}
        self.resolved_deps = {rule: list() for rule in self.graph}

    def exe(self, rule_name):
        '''
        executes rules and their dependencies in parallel reducing execution time
        '''
        process_to_execute = self.get_independent_deps(rule_name)
        name_to_process = {dep: self.graph[dep].exe_rule() for dep in process_to_execute}

        while True:

            for rule_name in list(name_to_process):
                if name_to_process[rule_name].poll() is not None:
                    if name_to_process[rule_name].poll() is not 0:
                        raise subprocess.CalledProcessError
                    rule = self.graph[rule_name]
                    del name_to_process[rule_name]
                    process_to_execute.remove(rule_name)
                    for parent in rule.dependents:
                        self.unresolved_deps[parent].remove(rule_name)
                        self.resolved_deps[parent].append(rule_name)
                        if not self.unresolved_deps[parent]:
                            process_to_execute.add(parent)
                            if self.graph[parent].command:
                                name_to_process[parent] = self.graph[parent].exe_rule()
                            else:
                                for dependent in self.graph[parent].dependents:
                                    process_to_execute.add(dependent)

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
            for dep in self.graph[vertex].dependencies:
                if dep not in visited:
                    stack.append(dep)
                    if not self.graph[dep].dependencies:
                        independent_deps.add(dep)
                    visited.add(dep)
        return independent_deps


class SerialExe():

    def __init__(self, graph_obj):
        self.graph_obj = graph_obj
        self.graph = graph_obj.rule_name_to_rule
        self.resolved = []


    def exe(self, rule_name):
        '''
        executes rules and their dependencies serially
        '''

        rule = self.graph[rule_name]
        for dep in rule.dependencies:
            if dep not in self.resolved:
                self.exe(dep)
        process = rule.exe_rule()
        if process:
            process.wait()
        self.resolved.append(rule)


class WatchChanges():

    def __init__(self, executor):
        self.executor = executor
        self.filepath_to_rule_name = dict()
        self.file_watch = dict()

    def watch_changes(self):
            while True:
                for root, _, files in os.walk(self.executor.graph_obj.base_addr):
                    if self.executor.graph_obj.RULE_FILE in files:
                        with open(os.path.join(root, self.executor.graph_obj.RULE_FILE)) as build_file:
                            rule_json = json.load(build_file)
                            for obj in rule_json:
                                if "files" in obj:
                                    for file in obj["files"]:
                                        self.check_file_changes(file, root)
                time.sleep(1)

    def check_file_changes(self, file, addr):
        file_edit_time = os.stat(os.path.join(addr, file)).st_mtime
        if file in self.file_watch:
            if self.file_watch[file] < file_edit_time:
                print(file, "changed...")
                print("recompiling files...")
                self.recompile_files(file)
                self.file_watch[file] = file_edit_time
        else:
            self.file_watch[file] = file_edit_time

    def recompile_files(self, file):
        '''runs actions of rules associated with the given file to recompile affected files'''
        self.executor.exe(self.filepath_to_rule_name[file])
        parents = set(self.executor.graph[self.filepath_to_rule_name[file]].dependents)
        while parents:
            resolved = set()
            next_parent_set = set()
            for parent in parents:
                self.executor.exe(parent)
                resolved.add(parent)
                for dependent in self.executor.graph[parent].dependents:
                    next_parent_set.add(dependent)
            parents = parents.union(next_parent_set).difference(resolved)

    def map_file_command(self, rule):
        '''maps files to commands to assist in implementing the watch feature'''
        if rule in self.filepath_to_rule_name.values():
            return
        files = input("Enter depended files for %s(Press Enter if none): " % (rule)).split()

        with open(os.path.join(self.executor.graph[rule].cwd, self.executor.graph_obj.RULE_FILE), 'r') as build_file:
            rule_json = json.load(build_file)
            for obj_index in range(len(rule_json)):
                if rule_json[obj_index]["name"] == self.executor.graph[rule].name:
                    rule_json[obj_index]["files"] = files
                    for file in files:
                        self.filepath_to_rule_name[file] = rule

        with open(os.path.join(self.executor.graph[rule].cwd, self.executor.graph_obj.RULE_FILE), 'w') as build_file:
            json.dump(rule_json, build_file)

        for dep in self.executor.graph[rule].dependencies:
            self.map_file_command(dep)
