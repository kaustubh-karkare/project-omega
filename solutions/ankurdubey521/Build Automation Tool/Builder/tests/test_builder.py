import unittest
import subprocess
from Builder.main import execute


class TestBuilder(unittest.TestCase):

    def test_compilation(self):
        path = 'filetree'
        execute('run', path)
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual(result.stdout, '1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n')
        execute('clean', path)


if __name__ == '__main__':
    unittest.main()
