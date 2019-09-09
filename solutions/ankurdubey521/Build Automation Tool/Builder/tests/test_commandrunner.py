import unittest
from Builder.lib.commandrunner import run


class MyTestCase(unittest.TestCase):
    def test_basic_command(self):
        command = "echo 'Hello World!'"
        exit_code = run(command)
        self.assertEqual(0, exit_code)

    def test_nonzero_exit_code(self):
        command = "exit 1"
        exit_code = run(command)
        self.assertEqual(1, exit_code)


if __name__ == '__main__':
    unittest.main()
