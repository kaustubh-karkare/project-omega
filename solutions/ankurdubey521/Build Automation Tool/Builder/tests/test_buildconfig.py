import unittest

from Builder.lib.buildconfig import BuildConfig


class TestJsonParser(unittest.TestCase):
    def setUp(self):
        json = [
            {
                "name": "clean",
                "deps": [
                    "algorithms/clean"
                ],
                "command": "rm -f test.o && rm -f test.exe"
            },
            {
                "name": "test",
                "files": [
                    "test.cpp"
                ],
                "command": "g++ -std=c++11 -c test.cpp"
            }
        ]
        self.config = BuildConfig(json)

    def test_build_clean_parses_correctly(self):
        command_clean = self.config.get_build_rule('clean')
        self.assertEqual(command_clean.get_name(), 'clean')
        self.assertEqual(command_clean.get_command(), 'rm -f test.o && rm -f test.exe')
        self.assertEqual(command_clean.get_dependencies(), ["algorithms/clean"])

    def test_build_test_parses_correctly(self):
        command_test = self.config.get_build_rule('test')
        self.assertEqual(command_test.get_name(), 'test')
        self.assertEqual(command_test.get_command(), 'g++ -std=c++11 -c test.cpp')
        self.assertEqual(command_test.get_files(), ["test.cpp"])

    def test_unknown_command_name_raises_correct_exception(self):
        self.assertRaises(BuildConfig.UnknownCommandException, self.config.get_build_rule, 'YOLO')


if __name__ == '__main__':
    unittest.main()
