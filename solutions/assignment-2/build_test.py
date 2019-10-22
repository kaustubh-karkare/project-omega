import unittest
import os
from build import Builder

class BuildToolTest(unittest.TestCase):

    tool = Builder()

    def test_cpp_example(self):
        self.assertEqual(self.tool.rule_exe("run", os.getcwd())[-1], "1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n")

    def test_checkparentfunction(self):
       self.assertEqual(self.tool.check_parent_rule("sort_bubble.cpp", os.getcwd()), "run")
       self.assertEqual(self.tool.check_parent_rule("test.cpp", os.getcwd()), "run")

if __name__ == '__main__':
    unittest.main()
