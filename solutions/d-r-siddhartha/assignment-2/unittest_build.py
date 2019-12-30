import unittest
import build
import tempfile
import os
from distutils.dir_util import copy_tree


class BuildToolTest(unittest.TestCase):

    BASE_ADDR = os.getcwd()

    def test_serial_build(self):
        '''
        Testing basic build functionality. The build tool should complete the actions of the dependencies
        before executing the root rule.
        '''

        RULE = "test_sort_merge"

        with tempfile.TemporaryDirectory() as TempDir:
            copy_tree(self.BASE_ADDR, TempDir)
            os.chdir(TempDir)
            BuildGraph = build.Graph()
            BuildGraph.create_graph()
            Executor = build.SerialExe(BuildGraph.rule_name_to_rule)
            Executor.exe(RULE)
            files = ["test.o", "algorithms/sort_merge.o", "test_sort_merge.exe"]
            for file in files:
                self.assertTrue(os.path.exists(os.path.join(TempDir, file)))
            os.chdir(self.BASE_ADDR)

    def test_parallel_build(self):

        RULE = "test_all"

        with tempfile.TemporaryDirectory() as TempDir:
            copy_tree(self.BASE_ADDR, TempDir)
            os.chdir(TempDir)
            BuildGraph = build.Graph()
            BuildGraph.create_graph()
            Executor = build.ParallelExe(BuildGraph.rule_name_to_rule)
            Executor.exe(RULE)
            files = ["test.o","algorithms/sort_merge.o", "algorithms/sort_bubble.o", "algorithms/sort_quick.o", "test_sort_bubble.exe", "test_sort_quick.exe", "test_sort_merge.exe"]
            for file in files:
                self.assertTrue(os.path.exists(os.path.join(TempDir, file)))
            os.chdir(self.BASE_ADDR)

    def test_circualar_dependency(self):

        RULE = "test_all"

        BuildGraph = build.Graph()
        BuildGraph.create_graph()
        self.assertFalse(BuildGraph.detect_circular_dependency(RULE))


if __name__ == "__main__":
    unittest.main()
