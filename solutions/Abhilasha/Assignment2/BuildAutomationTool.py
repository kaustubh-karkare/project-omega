import os
import json


class Action():
    
    def get_command(self, cwd, command, action):
        
        if command != "build":
            raise Exception('Command not recognized.')
            return
        else:
            self.get_action(cwd, action)
            return
        
        
    def get_action(self, cwd, action):
        
        os.chdir(cwd)
        action_found = False

        with open(os.path.join("build.json")) as json_file:
            all_text = json.load(json_file)
            
            for text in all_text:
                if text['name'] == action:
                    action_found = True
                    ActionGraph_obj = ActionGraph()
                    ActionGraph_obj.plot_graph(text, cwd)

            if action_found is False:
                raise Exception('Command not recognized.')
                return

        return
    
    
class ActionGraph():
    
     def __init__(self):
         
         self.executed_commands = set([])
    
    
     def plot_graph(self, text, cwd):
        
        if 'deps' in text:
            
            for dependency in text['deps']:
                
                if len(str(dependency).split('/')) == 2:
                    
                    dependency = str(dependency).split('/')[1]
                    with open(os.path.join("algorithms\\build.json")) as json_file:
                        all_text_new = json.load(json_file)
                        
                        for text_new in all_text_new:
                            if text_new['name'] == dependency:
                                os.chdir(cwd+"\\algorithms")
                                self.plot_graph(text_new, cwd)
                                
                else:
                    
                    with open(os.path.join("build.json")) as json_file:
                        all_text_new = json.load(json_file)
                        
                        for text_new in all_text_new:
                            if text_new['name'] == dependency:
                                os.chdir(cwd)
                                self.plot_graph(text_new, cwd)
        
        if 'command' in text:
                
                if text['command'] not in self.executed_commands:
                    os.system(text['command'])
                    self.executed_commands.add(text['command'])
                    os.chdir(cwd)
                                
        return
        