import argparser
import unittest
from typing import List
Vector = List[int]


class TestArgparser(unittest.TestCase):

    def test_key_name(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--key', type=int, nargs=1)
        parser.add_argument(name='--name', type=str, nargs=1)
        output = parser.arg_parse(['--key', '11', '--name', 'abcd'])
        self.assertEqual(output, '{"key": 11, "name": "abcd"}')
        output = parser.arg_parse(['--key', 'abcd'])
        self.assertEqual(str(output), 'Error : Invalid type of argument "abcd", invalid literal for int() with base 10: \'abcd\'.')
        output = parser.arg_parse(['--name', 'abcd', '--key', '-1520'])
        self.assertEqual(output, '{"name": "abcd", "key": -1520}')
        output = parser.arg_parse(['--name', 'abcd', 'xyz', '--key', '1520'])
        self.assertEqual(str(output), 'Error : --name expects exactly 1 arguments but 2 arguments are found.')

    def pos_int(self, arg: str) -> int:
        try:
            arg = int(arg)
            if arg < 0:
                raise ValueError(f'Excepted Positive integer')
            return arg
        except ValueError as e:
            raise e

    def test_key_name_modified(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--key', type=self.pos_int, nargs=1)
        parser.add_argument(name='--name', type=str, repeat=True)
        output = parser.arg_parse(['--key', '11', '--name', 'abcd'])
        self.assertEqual(output, '{"key": 11, "name": "abcd"}')
        output = parser.arg_parse(['--key', '-11', '--name', 'abcd'])
        self.assertEqual(str(output), 'Error : Invalid type of argument "-11", Excepted Positive integer.')
        output = parser.arg_parse(['--name', 'wxyz', '--key', '11', '--name', 'abcd', 'pqrs'])
        self.assertEqual(output, '{"name": ["wxyz", "abcd", "pqrs"], "key": 11}')
        output = parser.arg_parse(['--name', 'wxyz', '--key', '11', '--name', 'abcd', '--key', '123'])
        self.assertEqual(str(output), 'Error : --key is not allowed to repeat.')

    def test_mutually_exclusive_group(self):
        parser = argparser.ArgumentParser()
        parser.add_mutually_exclusive_group()
        parser.add_argument(name='--local', nargs=1)
        output = parser.arg_parse(['--local', '192.168.112.65'])
        self.assertEqual(output, '{"local": "192.168.112.65"}')
        parser.add_argument(name='--remote')
        output = parser.arg_parse(['--local', '192.168.112.65', '--remote'])
        self.assertEqual(str(output), "Error : ['local', 'remote'] options cannot appear together.")
        output = parser.arg_parse(['--remote', 'xyz'])
        self.assertEqual(output, '{"remote": "xyz"}')
        output = parser.arg_parse([])
        self.assertEqual(str(output), "Error : Atleast one option is required.")

    def mul(self, args: Vector) -> int:
        res = 1
        for i in args:
            res *= i
        return res

    def test_added_features(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--sum', action=sum, nargs='+', type=int)
        parser.add_argument(name='--max', action=max, nargs='+', type=int)
        parser.add_argument(name='--mul', action=self.mul, nargs=3, type=int)
        output = parser.arg_parse(['--sum', '1', '2', '3', '--max', '4', '6', '7', '12', '--mul', '2', '1', '3'])
        self.assertEqual(output, '{"sum": 6, "max": 12, "mul": 6}')
        output = parser.arg_parse(['--mul', '2', '10'])
        self.assertEqual(str(output), 'Error : --mul expects exactly 3 arguments but 2 arguments are found.')
        output = parser.arg_parse(['--sum', '--mul', '1', '2', '3'])
        self.assertEqual(str(output), 'Error : 1 or more arguments for the option --sum are required.')


if __name__ == '__main__':
    unittest.main()
