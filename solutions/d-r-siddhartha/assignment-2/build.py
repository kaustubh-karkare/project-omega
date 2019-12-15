import subprocess
import os
import sys
import json

class Builder(object):
    '''
    main class dealing with rule execution
    '''
    def __init__(self):
        self.graph_dict = dict()
        self.graph_loc = {"base_addr" : os.getcwd()}

    def rule_exe(self, rule, resolved, unresolved):
        unresolved.append(rule)
        rule_obj = self.graph_dict[rule]
        for dep in rule_obj.deps:
            if dep not in resolved:
                if dep in unresolved:
                    raise Exception("Circular dependency detected!")
                self.rule_exe(dep, resolved, unresolved)
        if rule_obj.command:
            print(rule_obj.name)
            os.chdir(self.graph_loc[rule])
            subprocess.run(rule_obj.command, shell=True)
            print(rule_obj.command, "executed...")
            os.chdir(self.graph_loc["base_addr"])

        resolved.append(rule)
        unresolved.remove(rule)

    def create_graph(self):
        for root, dirs, files in os.walk(os.getcwd()):
            if 'build.json' in files:
                with open(root + '/build.json') as build_file:
                    rule_json = json.load(build_file)
                    for obj in rule_json:
                        rule_name = root.partition(self.graph_loc["base_addr"])[-1][1:] + "/" + obj["name"] if root != self.graph_loc["base_addr"] else obj["name"]
                        self.graph_dict[rule_name] = Rule(obj["name"])
                        self.graph_loc[rule_name] = root
                        if "deps" in obj:
                            for dep in obj["deps"]:
                                self.graph_dict[rule_name].addDeps(dep)
                        if "command" in obj:
                            self.graph_dict[rule_name].command = obj["command"]

class Rule(object):

    def __init__(self, name):
        self.name = name
        self.deps = list()
        self.command = None

    def addDeps(self, dep):
        self.deps.append(dep)

if __name__ == "__main__":
    build_obj = Builder()
    rule = sys.argv[1]
    build_obj.create_graph()
    build_obj.rule_exe(rule, [], [])
