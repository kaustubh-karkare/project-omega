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
from enum import Enum


class Status(Enum):
    
    not_started = 1
    ready = 2
    processing = 3
    done = 4


class ActionGraph():    

    '''loads commands, dependencies and initialises the status for all the actions from all build.json files.'''    

    def __init__(self):

        self.all_action_commands = {}
        self.all_action_dependencies = {}

        
    def create_action_map(self, root_dir):

        for filename in Path(root_dir).rglob('build.json'):           
            path_elements = str(relpath(filename, root_dir)).split(os.path.sep)          
            rel_location = os.path.sep.join(path_elements[:-1])
            with open(filename) as json_file:
                all_data = json.load(json_file)
            for data in all_data:
                if rel_location != '':
                    action = rel_location+'/'+data['name']
                else:
                    action = data['name']
                self.all_action_commands[action] = data.get('command')
                self.all_action_dependencies[action] = data.get('deps')  
        return self.all_action_commands, self.all_action_dependencies

            
class Action():
    
    def __init__(self):

        self.current_action_status = {}
        self.current_action_commands = {}
        self.current_action_dependencies = {}
        self.dependents = {}
        
    
    def action_sequence(self, root, action):
            
        graph = ActionGraph()
        self.all_action_commands, self.all_action_dependencies = graph.create_action_map(root)
        
        if action not in self.all_action_commands:
            raise Exception('Command not recognized.')
            
        self.get_dependencies(action)
        self.store_dependents_for_all_action()
        self.initialize_dependencies_status(action)
        
        return (self.current_action_status,
                self.current_action_commands,
                self.current_action_dependencies,
                self.dependents)
    

    def get_dependencies(self, action):         

        '''stores the status, commands, dependencies of the action to be executed and all its dependencies'''       

        self.current_action_status[action] = Status.not_started
        self.current_action_commands[action] = self.all_action_commands[action]
        self.current_action_dependencies[action] = self.all_action_dependencies[action]    

        if not self.all_action_dependencies[action] is None:
            for name in self.all_action_dependencies[action]:
                self.get_dependencies(name)
        return


    def store_dependents_for_all_action(self):

        for action in self.current_action_status:
            self.dependents.setdefault(action, [])               

        for action in self.current_action_status:
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
             self.current_action_status[action] = Status.ready

         else:
             for dep in self.current_action_dependencies[action]:                          
                 self.initialize_dependencies_status(dep)                     

         return                

              
class ActionExecutor():

    def __init__(self, root_dir):

        self.root_dir = root_dir
        self.ongoing_subprocesses = []
        self.action_name_for_ongoing_subprocess = []
        self.action_name = ''
        self.pending_actions = []

        
    def execute(self, build, action):

        if build != 'build':
            raise Exception('Command not recognized.')
            
        action_obj = Action()
        (self.current_action_status,
        self.current_action_commands,
        self.current_action_dependencies,
        self.dependents) = action_obj.action_sequence(self.root_dir, action)
        
        self.initialize_pending_actions()
        self.execute_commands()

        return
    
    
    def initialize_pending_actions(self):

        for action in self.current_action_status:
            self.pending_actions.append(action)

        return


    def update_dependencies_status(self, action):

         ''' updates the status of the actions with all deps executed as ready '''        

         total_no_of_dependencies = len(self.current_action_dependencies[action])
         no_of_dependencies_done = 0
         for dep in self.current_action_dependencies[action]:         
             if self.current_action_status[dep] == Status.done:
                 no_of_dependencies_done += 1
         if no_of_dependencies_done == total_no_of_dependencies:
             self.current_action_status[action] = Status.ready

         return


    def execute_commands(self):

        while len(self.pending_actions) != 0:
            any_action_has_no_command = False
            for name in self.current_action_status:
                 if self.current_action_status[name] == Status.ready:
                     self.current_action_status[name] = Status.processing
                     cwd = os.getcwd()
                     if '/' in name:
                         loc = name[:name.rindex('/')]
                     else:
                         loc = ''
                     if loc != '':
                         cwd = cwd+os.path.sep+loc
                     command = self.current_action_commands[name]
                     if command is None:                         
                         any_action_has_no_command = True
                         self.current_action_status[name] = Status.done
                         self.pending_actions.remove(name)
                         if len(self.dependents[name]) != 0:
                             for action in self.dependents[name]:
                                 if self.current_action_status[action] == Status.not_started:
                                     self.update_dependencies_status(action)
                         break
                     else:
                         process = subprocess.Popen(command, shell=True, cwd=cwd)
                         self.ongoing_subprocesses.append(process)
                         self.action_name_for_ongoing_subprocess.append(name)

            if any_action_has_no_command:
                continue

            while True:                
                 any_subprocess_completed = False                
                 for process, action in zip(self.ongoing_subprocesses, self.action_name_for_ongoing_subprocess):
                     if not process.poll() is None:
                         any_subprocess_completed = True
                         break     

                 if any_subprocess_completed:
                     break
                 time.sleep(1)

            self.ongoing_subprocesses.remove(process)
            self.action_name_for_ongoing_subprocess.remove(action)
            self.current_action_status[action] = Status.done
            self.pending_actions.remove(action)
            
            if len(self.dependents[action]) != 0:
                for name in self.dependents[action]:
                    if self.current_action_status[name] == Status.not_started:
                        self.update_dependencies_status(name)

        return 
    