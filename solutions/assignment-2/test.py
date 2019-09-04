import unittest
import subprocess


class TestBuildAutomation(unittest.TestCase):

    def test_test1(self):
        cmd = 'cd test1 && python build.py clean run'
        result = subprocess.check_output(cmd, shell=True)
        self.assertEqual(result, b'Tested sort_bubble sort_merge sort_quick')


if __name__ == '__main__':
    unittest.main()
