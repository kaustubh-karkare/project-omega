import unittest
from Builder.lib.buildconfig import BuildConfig


class TestJsonParser(unittest.TestCase):
    def test_sample_json_parser_correctly(self):
        json_path = 'json/test1.json'
        config = BuildConfig(json_path)
        assert config.command_names() == ['clean', 'test']
        assert config.deps('clean') == ["algorithms/clean"]
        assert config.command('clean') == "rm -f test.o && rm -f test.exe"


if __name__ == '__main__':
    unittest.main()
