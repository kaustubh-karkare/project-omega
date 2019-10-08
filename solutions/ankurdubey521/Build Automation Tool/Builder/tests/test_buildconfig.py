import unittest
import tempfile
from Builder.lib.buildconfig import BuildConfig
from Builder.global_constants import GlobalConstants


class TestJsonParser(unittest.TestCase):
    def setUp(self):
        json_string = '[{"name":"clean","deps":["algorithms/clean"],"command":"rm -f test.o && rm -f test.exe"}' + \
                     ',{"name":"test","files":["test.cpp"],"command":"g++ -std=c++11 -c test.cpp"}]'
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file_path = tmpdir + "/" + GlobalConstants.CONFIG_FILE_NAME
            with open(json_file_path, 'w') as json_handle:
                json_handle.write(json_string)
            self.config = BuildConfig(tmpdir)

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

    def test_unknown_command_name_raises_correct_exception(self):
        self.assertRaises(BuildConfig.UnknownCommandException, self.config.get_command, 'YOLO')


if __name__ == '__main__':
    unittest.main()
