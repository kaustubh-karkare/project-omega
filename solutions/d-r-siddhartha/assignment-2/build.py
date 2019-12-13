import subprocess
import argparse
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
        for dep in rule.deps:
            if dep not in resolved:
                if dep in unresolved:
                    raise Exception("Circular dependency detected! %s depends on %s" % (rule.name, dep.name))
                rule_exe(dep, resolved, unresolved)
        if rule.command:
            if rule.name in self.graph_loc:
                os.chdir(self.graph_loc[rule.name])
                subprocess.run(rule.command, shell=True)
                #print(rule.command, "executed...")
                os.chdir(self.graph_loc["base_addr"])
            else:
                subprocess.run(rule.command, shell=True)
                #print(rule.command, "executed...")
        resolved.append(rule)
        unresolved.remove(rule)

    def create_graph(self, build_file):
        rule_json = json.load(build_file)
        for obj in rule_json:
            self.graph_dict[obj["name"]] = Rule(obj["name"])
            #print(obj["name"], "created successfully...")
            if "deps" in obj:
                for dep in obj["deps"]:
                    self.graph_dict[obj["name"]].addDeps(dep)
                    if "command" in obj:
                        self.graph_dict[obj["name"]].command = obj["command"]

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
    for root, dirs, files in os.walk(os.getcwd()):
        if 'build.json' in files:
            os.chdir(root)
            with open('build.json') as build_file:
                build_obj.create_graph(build_file)
    build_obj.rule_exe(build_obj.graph_dict[rule], [], [])
    #print(build_obj.graph_dict["test"].deps)
