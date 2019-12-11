# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:36:59 2019

@author: Abhilasha
"""

import os
import json
import threading


class ActionGraph():  
    
    '''loads name, action and dependencies from build.json'''
    
    def __init__(self,root_dir):
        
        self.root_dir = root_dir
        

    def get_command_to_be_executed(self, command, action):
    
        os.chdir(self.root_dir)
        action_found = False
        with open(self.root_dir+os.path.sep+"build.json") as json_file:
            all_text = json.load(json_file)            
            for text in all_text:                
                if text['name'] == action:
                    order = 0                   
                    action_found = True
                    Action_obj = Action()
                    Action_obj.compute_execution_order(text, self.root_dir, order)
                    Action_obj.execute_commands()
            if action_found is False:
                raise Exception('Command not recognized.')
                return
        return

  
class Action():
    
     '''computes the order of execution and executes the commands'''

     def __init__(self):
     
        self.commands = []
        self.working_directories = []       
        self.orders = []
        

     def compute_execution_order(self, text, cwd, order):

        if 'deps' in text:
            for dependency in text['deps']:
                if len(str(dependency).split('/')) == 2:        
                    next_json_file_loc = os.path.join(str(dependency).split('/')[0]+os.path.sep+"build.json")
                    dependency = str(dependency).split('/')[1]
                    with open(next_json_file_loc) as json_file:
                        all_text_new = json.load(json_file)                      
                        for text_new in all_text_new:                            
                            if text_new['name'] == dependency:
                                self.compute_execution_order(text_new, cwd+os.path.sep+"algorithms", order+1)
                else:
                    with open(os.path.join("build.json")) as json_file:
                        all_text_new = json.load(json_file)
                        for text_new in all_text_new:                            
                            if text_new['name'] == dependency:
                                self.compute_execution_order(text_new, cwd, order+1)
        if 'command' in text:                
            if text['command'] not in self.commands:                
                self.commands.append(text['command'])
                self.working_directories.append(cwd)
                self.orders.append(order)
        return
   

     def process(self, command, work_dir):

        os.chdir(work_dir)
        os.system(command)
        return
            

     def execute_commands(self):
     
        order_count = max(self.orders)        
        for cnt in range(order_count+1):           
            i = order_count-cnt         
            thread_list = []
            count = 0
            for command, work_dir, order in zip(self.commands, self.working_directories, self.orders):
                if order == i:               
                    thread = threading.Thread(target = self.process, args = (command, work_dir))
                    thread_list.append(thread)
                    thread_list[count].start()
                    count += 1
            for thread in thread_list:
                thread.join()   
        return
 