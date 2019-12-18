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
            rel_location = relpath(filename,self.root_dir)
            if len(str(rel_location).split(os.path.sep)) == 1:
                rel_location = ''
            else:
                rel_location = str(rel_location).split(os.path.sep)[0]
            with open(filename) as json_file:
                all_data = json.load(json_file)
                for data in all_data:
                    if rel_location != '':
                        action = rel_location+'/'+data['name']
                    else:
                        action = data['name']
                    self.all_action_status[action] = 'not started'
                    if 'command' in data:
                        self.all_action_commands[action] = data['command']
                    else:
                        self.all_action_commands[action] = 'none'                
                    if 'deps' in data:
                        self.all_action_dependencies[action] = data['deps']
                    else:
                        self.all_action_dependencies[action] = 'none'

            
    def get_command_to_be_executed(self, build, action):
        
        if action not in self.all_action_status:
            raise Exception('Command not recognized.')
            return        
        else:
            Action_obj = Action(self.all_action_status, self.all_action_commands, self.all_action_dependencies)
            Action_obj.get_dependencies(action)
            Action_obj.update_dependencies_status(action)
            Action_obj.execute_commands()
            return 
                    
              
class Action():
    

     def __init__(self, all_action_status, all_action_commands, all_action_dependencies):
     
        self.all_action_status = all_action_status
        self.all_action_commands = all_action_commands
        self.all_action_dependencies = all_action_dependencies        
        self.current_action_status = {}
        self.current_action_commands = {}
        self.current_action_dependencies = {}              
        self.ongoing_subprocesses = []
        self.action_name_for_ongoing_subprocess = []
        
        
     def get_dependencies(self, action):
         
        '''stores the status, commands, dependencies of the action to be executed and all its dependencies'''
        
        self.current_action_status[action] = self.all_action_status[action]
        self.current_action_commands[action] = self.all_action_commands[action]
        self.current_action_dependencies[action] = self.all_action_dependencies[action]       
        if self.all_action_dependencies[action] != 'none':       
            for name in self.all_action_dependencies[action]:
                self.get_dependencies(name)                    
        return
                   
        
     def update_dependencies_status(self, action):
         
         ''' updates the status of the actions- ready or processing or done '''
         
         if self.current_action_dependencies[action] == 'none':
             self.current_action_status[action] = 'ready'
         else:             
             total_no_of_dependencies = len(self.current_action_dependencies[action])
             no_of_dependencies_done = 0;
             for dep in self.current_action_dependencies[action]:                             
                 if self.current_action_status[dep] == 'not started':
                     self.update_dependencies_status(dep)
                 if self.current_action_status[dep] == 'done':
                     no_of_dependencies_done += 1      
             if no_of_dependencies_done == total_no_of_dependencies:
                 self.current_action_status[action] = 'ready'                  
         return


                    
     def execute_commands(self):
        
         for name in self.current_action_status:
             if(self.current_action_status[name] == 'ready'):                 
                 self.current_action_status[name] = 'processing'
                 cwd = os.getcwd()
                 if '/' in name:            
                     loc = name[:name.rindex('/')]                     
                 else:                     
                     loc = ''   
                                      
                 if self.current_action_commands[name] != 'none':
                     if loc != '':
                         os.chdir(cwd+os.path.sep+loc)
                     command = str(self.current_action_commands[name])
                     p = subprocess.Popen(command, shell=True)
                     os.chdir(cwd)
                     self.ongoing_subprocesses.append(p)
                     self.action_name_for_ongoing_subprocess.append(name)
                                         
                 else:                     
                     self.current_action_status[name] = 'done'                     
                     for name in self.current_action_status:
                         if(self.current_action_status[name] == 'not_started'):
                             self.update_dependencies_status(name)
                     self.execute_commands()
                              
         while not len(self.ongoing_subprocesses) == 0:
             
             any_subprocess_completed = False    
             for p, action in zip(self.ongoing_subprocesses, self.action_name_for_ongoing_subprocess):
                 if not(p.poll() is None):
                     any_subprocess_completed = True
                     break
                 else:
                     continue
                     
             if any_subprocess_completed == True:
                 self.ongoing_subprocesses.remove(p)
                 self.action_name_for_ongoing_subprocess.remove(action)
                 self.current_action_status[action] = 'done'
                 for name in self.current_action_status:
                     if(self.current_action_status[name] == 'not started'):     
                         self.update_dependencies_status(name)                             
                 self.execute_commands() 
             else:
                 time.sleep(1)
         return
                  