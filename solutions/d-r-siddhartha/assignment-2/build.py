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
        unresolved.append(rule.name)
        for dep in rule.deps:
            if dep not in resolved:
                if dep in unresolved:
                    raise Exception("Circular dependency detected! %s depends on %s" % (rule.name, dep.name))
                self.rule_exe(self.graph_dict[dep.rpartition("/")[-1], resolved, unresolved)
        if rule.command:
            if rule.name in self.graph_loc:
                os.chdir(self.graph_loc[rule.name])
                print(rule.command, "executed...")
                subprocess.run(rule.command, shell=True)
                os.chdir(self.graph_loc["base_addr"])
            else:
                print(rule.command, "executed...")
                subprocess.run(rule.command, shell=True)

        resolved.append(rule.name)
        unresolved.remove(rule.name)

    def create_graph(self, build_file):
        rule_json = json.load(build_file)
        for obj in rule_json:
            self.graph_dict[obj["name"]] = Rule(obj["name"])
            #if obj["name"] == "test":
                #print(obj["command"])
            if "deps" in obj:
                for dep in obj["deps"]:

                    self.graph_dict[obj["name"]].addDeps(dep)
                    #print("adding dependency", self.graph_dict[obj["name"]].deps)
            if "command" in obj:
                #print(obj["name"])
                self.graph_dict[obj["name"]].command = obj["command"]
                        #print(self.graph_dict[obj["name"]].command)

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
            with open(root + '/build.json') as build_file:
                build_obj.create_graph(build_file)
    #print(build_obj.graph_dict)
    build_obj.rule_exe(build_obj.graph_dict[rule], [], [])
