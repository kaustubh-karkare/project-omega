import json
import os
from queue import Queue
from typing import Any, List, Dict, Union
Vector = List[str]


class BuildAutomationError(Exception):

    def __init__(self, message: str):
        super(BuildAutomationError, self).__init__(message)
        self.message: str = message


class Option(object):
    """Option stores all the possible build options provided in build configuration files"""

    def __init__(self, properties: Dict[str, Any], command_path: str):
        self.name: str = properties['name']
        self.command: str = 'cd {} && {}'.format(command_path, properties['command'])
        self.file: Union[None, Vector] = None
        self.deps: Union[None, Vector] = None
        if 'files' in properties:
            self.file = properties['files']
        if 'deps' in properties:
            self.deps = properties['deps']

    def execute(self, build_options: Dict[str, Any]) -> None:
        options_to_execute: Vector = Graph.topological_sort(self.name, build_options)
        options_to_execute.reverse()  # Since the list contains values from high to low dependency, we reverse it
        for option in options_to_execute:
            os.system(build_options[option].command)


class Graph(object):
    """Graph supports static methods like depth first search and topological sorting to resolve the dependencies"""

    @staticmethod
    def depth_first_search(source: str, visited: Dict[str, bool], indegree: Dict[str, int], build_options: Dict[str, Option]) -> None:
        visited[source] = True
        indegree[source] = 0
        try:
            option: Option = build_options[source]
        except KeyError:
            raise BuildAutomationError(f'Invalid option "{source}" found')
        if option.deps is not None:
            for child in option.deps:
                if child not in visited:
                    Graph.depth_first_search(child, visited, indegree, build_options)
                indegree[child] += 1

    @staticmethod
    def topological_sort(source: str, build_options: Dict[str, Option]) -> Vector:
        indegree: Dict[str, int] = dict()
        visited: Dict[str, bool] = dict()
        Graph.depth_first_search(source, visited, indegree, build_options)
        if indegree[source] != 0:  # Source must have indegree == 0
            raise BuildAutomationError('Invalid dependencies found (Circular dependencies exists)')
        topo_sort: Vector = list()
        que: Queue[str] = Queue(maxsize=0)
        que.put(source)
        while not que.empty():
            try:
                next_option: Option = build_options[que.get()]
            except KeyError:
                raise BuildAutomationError(f'Invalid option "{source}" found')
            topo_sort.append(next_option.name)
            if next_option.deps is not None:
                for child in next_option.deps:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        que.put(child)
        for option in indegree:
            if indegree[option] != 0:   # All the values should have indegree == 0 if the dependencies form a DAG
                raise BuildAutomationError('Invalid dependencies found (Circular dependencies exists)')
        return topo_sort


class Build(object):
    """Build scans a given directory and stores all the possible build options """

    def __init__(self, path: str):
        self.build_options: Dict[str, Option] = dict()
        self.scan(path=path, relative_path='')

    def scan(self, path: str, relative_path: str) -> None:
        for file in os.listdir(path):
            file_path: str = os.path.join(path, file)
            if os.path.isdir(file_path):
                self.scan(path=file_path, relative_path=f'{relative_path}{file}\\')
            else:
                if file == 'build.json':
                    json_file: Any = open(file_path)
                    json_dict: Any = json.loads(json_file.read())
                    for properties in json_dict:
                        properties['name'] = relative_path + properties['name']
                        if properties['name'] not in self.build_options:
                            self.build_options[properties['name']] = Option(properties=properties, command_path=path)
                        else:
                            name = properties['name']
                            raise BuildAutomationError(f'{name} has multifile entities in different build configuration files which conflicts')

    def execute(self, options: Vector) -> None:
        for option in options:
            try:
                self.build_options[option].execute(self.build_options)
            except KeyError:
                raise BuildAutomationError(f'Invalid option "{option}" provided')
