import os
import json
import subprocess
import threading
import time

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
                    ActionGraph_obj.execute_commands()

            if action_found is False:
                
                raise Exception('Command not recognized.')
                return

        return
    
    
class ActionGraph():
    
     def __init__(self):
         
        self.commands = []
        self.working_directories = []
    
    
     def plot_graph(self, text, cwd):
        
        if 'deps' in text:
            
            for dependency in text['deps']:
                
                if len(str(dependency).split('/')) == 2:
                    
                    dependency = str(dependency).split('/')[1]
                    with open(os.path.join("algorithms\\build.json")) as json_file:
                        
                        all_text_new = json.load(json_file)                      
                        for text_new in all_text_new:
                            
                            if text_new['name'] == dependency:
                                
                                self.plot_graph(text_new, cwd+"\\algorithms")
                                
                else:
                    
                    with open(os.path.join("build.json")) as json_file:
                        
                        all_text_new = json.load(json_file)
                        for text_new in all_text_new:
                            
                            if text_new['name'] == dependency:
                                
                                self.plot_graph(text_new, cwd)
        
        if 'command' in text:
                
            if text['command'] not in self.commands:
                
                self.commands.append(text['command'])
                self.working_directories.append(cwd)
                                
        return
    
     def process(self, command, work_dir):
         
        os.chdir(work_dir)
        os.system(command)
        return
            
        
     def execute_commands(self):
       
        thread_list = []
        count = 0
        for command, work_dir in zip(self.commands, self.working_directories):
         
            thread = threading.Thread(target = self.process, args = (command, work_dir))
            thread_list.append(thread)
            time.sleep(2)
            thread_list[count].start()
            count += 1
      
        for thread in thread_list:
            
            thread.join()   
            
        return

