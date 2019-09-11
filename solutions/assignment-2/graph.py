from typing import List, Dict, Any
from queue import Queue


class GraphError(Exception):

    def __init__(self, message: str):
        super(GraphError, self).__init__(message)
        self.message: str = message


class Graph(object):
    """Graph supports static methods like depth first search and topological sorting to resolve the dependencies"""

    def __init__(self, adjacency_list: Dict[Any, List[Any]]):
        self.adjacency_list = adjacency_list

    def depth_first_search(self) -> List[Any]:
        processed: Dict[Any, int] = {key: -1 for key in self.adjacency_list}
        dfs_list: List[Any] = list()
        for node in processed:
            if processed[node] == -1:
                self.dfs(node, processed, dfs_list)
        dfs_list.reverse()
        return dfs_list

    def dfs(self, node: Any, processed: Dict[Any, int], dfs_list: List[Any]) -> None:
        processed[node] = 0
        for child_node in self.adjacency_list[node]:
            if child_node in processed:
                if processed[child_node] == -1:
                    self.dfs(child_node, processed, dfs_list)
                if processed[child_node] == 0:
                    raise GraphError('Cyclic dependencies found')
            else:
                raise GraphError(f'Undefined dependencies found "{child_node}"')
        dfs_list.append(node)
        processed[node] = 1
