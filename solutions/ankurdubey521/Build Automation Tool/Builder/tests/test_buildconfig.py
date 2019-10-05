import unittest
from Builder.lib.buildconfig import BuildRule, BuildConfig


class TestJsonParser(unittest.TestCase):

    def setUp(self):
        self.config = BuildConfig('json')

    def test_build_clean_parses_correctly(self):
        command_clean = self.config.get_command('clean')
        self.assertEqual(command_clean.get_name(), 'clean')
        self.assertEqual(command_clean.get_command_string(), 'rm -f test.o && rm -f test.exe')
        self.assertEqual(command_clean.get_dependencies(), ["algorithms/clean"])

    def test_build_test_parses_correctly(self):
        command_test = self.config.get_command('test')
        self.assertEqual(command_test.get_name(), 'test')
        self.assertEqual(command_test.get_command_string(), 'g++ -std=c++11 -c test.cpp')
        self.assertEqual(command_test.get_files(), ["test.cpp"])

    def test_no_deps_throws_correct_exception(self):
        command_test = self.config.get_command('test')
        self.assertRaises(BuildRule.NoDependenciesException, command_test.get_dependencies)

    def test_no_files_throws_correct_exception(self):
        command_clean = self.config.get_command('clean')
        self.assertRaises(BuildRule.NoFilesException, command_clean.get_files)

    def test_unknown_command_name_raises_correct_exception(self):
        self.assertRaises(BuildConfig.UnknownCommandException, self.config.get_command, 'YOLO')


if __name__ == '__main__':
    unittest.main()
