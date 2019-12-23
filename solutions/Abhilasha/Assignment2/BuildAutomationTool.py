# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:36:59 2019

@author: Abhilasha
"""

import os
import json
import subprocess
from pathlib import Path
from os.path import relpath
import time
 

class ActionGraph():
    
    '''loads commands, dependencies and initialises the status for all the actions from all build.json files.'''
    
    def __init__(self, root_dir):
        
        self.root_dir = root_dir
        self.all_action_status = {}
        self.all_action_commands = {}
        self.all_action_dependencies = {}
        
    def create_action_map(self):
        
        for filename in Path(self.root_dir).rglob('*.json'):
            
            if str(filename).endswith('\\build.json'):
                path_elements = str(relpath(filename, self.root_dir)).split(os.path.sep)          
                rel_location = os.path.sep.join(path_elements[:-1])
                with open(filename) as json_file:
                    all_data = json.load(json_file)
                for data in all_data:
                    if rel_location != '':
                        action = rel_location+'/'+data['name']
                    else:
                        action = data['name']
                    self.all_action_status[action] = 'not started'
                    self.all_action_commands[action] = data.get('command')
                    self.all_action_dependencies[action] = data.get('deps')  
        return

            
    def get_command_to_be_executed(self, build, action):
        
        if build != 'build':
            raise Exception('Command not recognized.')
            
        if action not in self.all_action_status:
            raise Exception('Command not recognized.')
                  
        else:
            Action_obj = ActionExecutor(self.all_action_status, self.all_action_commands, self.all_action_dependencies)
            Action_obj.get_dependencies(action)
            Action_obj.store_dependents_for_all_action()
            Action_obj.initialize_dependencies_status(action)
            Action_obj.execute_commands()
            return
                    
              
class ActionExecutor():
    

    def __init__(self, all_action_status, all_action_commands, all_action_dependencies):
     
        self.all_action_status = all_action_status
        self.all_action_commands = all_action_commands
        self.all_action_dependencies = all_action_dependencies
        self.current_action_status = {}
        self.current_action_commands = {}
        self.current_action_dependencies = {}
        self.dependents = {}
        self.ongoing_subprocesses = []
        self.action_name_for_ongoing_subprocess = []
        self.action_name = ''
        
        
    def get_dependencies(self, action):
         
        '''stores the status, commands, dependencies of the action to be executed and all its dependencies'''
        
        self.current_action_status[action] = self.all_action_status[action]
        self.current_action_commands[action] = self.all_action_commands[action]
        self.current_action_dependencies[action] = self.all_action_dependencies[action]    
        if not self.all_action_dependencies[action] is None:
            for name in self.all_action_dependencies[action]:
                self.get_dependencies(name)
        return
    
                   
    def store_dependents_for_all_action(self):
         
        for action in self.current_action_status.keys():
            self.dependents.setdefault(action, [])
               
        for action in self.current_action_status.keys():
            self.action_name = action
            self.get_dependents(action)
        return
                       
            
    def get_dependents(self, action):
         
         if not self.all_action_dependencies[action] is None:                 
            for dep in self.all_action_dependencies[action]:
                if self.action_name not in self.dependents[dep]:
                    self.dependents[dep].append(self.action_name)                               
                self.get_dependents(dep)
         return
     
        
    def initialize_dependencies_status(self, action):
         
         ''' initialize the status of the actions with no deps as ready '''
         
         if self.current_action_dependencies[action] is None:
             self.current_action_status[action] = 'ready'
         else:
             for dep in self.current_action_dependencies[action]:                          
                 self.initialize_dependencies_status(dep)                     
         return
     
        
    def update_dependencies_status(self, action):
         
         ''' updates the status of the actions with all deps executed as ready '''
        
         total_no_of_dependencies = len(self.current_action_dependencies[action])
         no_of_dependencies_done = 0
         for dep in self.current_action_dependencies[action]:         
             if self.current_action_status[dep] == 'done':
                 no_of_dependencies_done += 1
         if no_of_dependencies_done == total_no_of_dependencies:
             self.current_action_status[action] = 'ready'
         return

                    
    def execute_commands(self):
        
         for name in self.current_action_status:
             if self.current_action_status[name] == 'ready':
                 self.current_action_status[name] = 'processing'
                 cwd = os.getcwd()
                 if '/' in name:
                     loc = name[:name.rindex('/')]
                 else:
                     loc = ''
                                      
                 if not self.current_action_commands[name] is None:
                     if loc != '':
                         cwd = cwd+os.path.sep+loc
                     command = str(self.current_action_commands[name])
                     p = subprocess.Popen(command, shell=True, cwd=cwd)
                     self.ongoing_subprocesses.append(p)
                     self.action_name_for_ongoing_subprocess.append(name)
                                         
                 else:
                     self.current_action_status[name] = 'done'
                     if len(self.dependents[name]) != 0:
                         for action in self.dependents[name]:
                             if(self.current_action_status[action] == 'not started'):
                                 self.update_dependencies_status(action)                                  
                         self.execute_commands()
                    
                              
         while not len(self.ongoing_subprocesses) == 0:
             
             any_subprocess_completed = False
             for p, action in zip(self.ongoing_subprocesses, self.action_name_for_ongoing_subprocess):
                 if not p.poll() is None:
                     any_subprocess_completed = True
                     break
                 else:
                     continue
                     
             if any_subprocess_completed == True:
                 self.ongoing_subprocesses.remove(p)
                 self.action_name_for_ongoing_subprocess.remove(action)
                 self.current_action_status[action] = 'done'
                 if len(self.dependents[action]) != 0:
                     for name in self.dependents[action]:
                         if self.current_action_status[name] == 'not started':
                             self.update_dependencies_status(name)                                  
                     self.execute_commands()
             else:
                 time.sleep(1)
         return
