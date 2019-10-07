from typing import List, Dict, TypeVar
from queue import Queue

T = TypeVar('T')


class TopologicalSort:
    class GraphContainsCycleException(Exception):
        pass

    @staticmethod
    def sort(graph_adj_list: Dict[T, List[T]]) -> List[T]:
        toposort = []
        visited = {}
        queue = Queue()
        in_degree = {}

        # Calculate  In-Degree of Each Vertex
        for source_node in graph_adj_list:
            visited[source_node] = False
            for dest_node in graph_adj_list[source_node]:
                visited[dest_node] = False
                if dest_node in in_degree:
                    in_degree[dest_node] = in_degree[dest_node] + 1
                else:
                    in_degree[dest_node] = 1

        # Find all vertices that have 0 In-degree.
        for source_node in graph_adj_list:
            if source_node not in in_degree:
                queue.put(source_node)

        # BFS
        while not queue.empty():
            front = queue.get()
            visited[front] = True
            toposort.append(front)
            if front in graph_adj_list:
                for dest_node in graph_adj_list[front]:
                    if not visited[dest_node]:
                        in_degree[dest_node] = in_degree[dest_node] - 1
                        if in_degree[dest_node] == 0:
                            queue.put(dest_node)

        # If any vertex exists whose In-Degree has not been exhausted, then graph must contain a cycle
        for node in in_degree:
            if in_degree[node] != 0:
                raise TopologicalSort.GraphContainsCycleException()

        return toposort

