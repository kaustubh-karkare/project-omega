import unittest

from Builder.lib.algorithms import TopologicalSort


class TestTopologicalSort(unittest.TestCase):
    def test_correct_toposort_returned_for_dag(self):
        graph_adj_list = {
            0: [1, 3],
            1: [2, 3],
            2: [3, 4, 5],
            3: [4, 5],
            4: [5]
        }
        toposort = TopologicalSort.sort(graph_adj_list)
        self.assertEqual([0, 1, 2, 3, 4, 5], toposort)

    def test_exception_thrown_if_graph_contains_cycle(self):
        graph_adj_list = {
            0: [1, 3],
            1: [2, 3],
            2: [3, 4, 5],
            3: [4, 5],
            4: [1, 5]
        }
        self.assertRaises(TopologicalSort.GraphContainsCycleException, TopologicalSort.sort, graph_adj_list)


if __name__ == '__main__':
    unittest.main()
