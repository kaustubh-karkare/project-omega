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

        output = parser.arg_parse(['--name', 'abcd', '--key', '-1520'])
        self.assertEqual(output, '{"name": "abcd", "key": -1520}')

    def pos_int(self, arg: str) -> int:
        try:
            arg = int(arg)
            if arg < 0:
                raise ValueError(f'Excepted Positive integer')
            return arg
        except ValueError as e:
            raise e

    def test_type(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--key', type=self.pos_int, nargs=1)
        parser.add_argument(name='--integer', type=int, nargs=1)

        output = parser.arg_parse(['--key', '123', '--integer', '-321'])
        self.assertEqual(output, '{"key": 123, "integer": -321}')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--key', 'abcd'])
        self.assertEqual(str(context.exception), 'Error : Invalid type of argument "abcd", invalid literal for int() with base 10: \'abcd\'.')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--key', '-123'])
        self.assertEqual(str(context.exception), 'Error : Invalid type of argument "-123", Excepted Positive integer.')

    def test_number_of_arguments(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--integers', type=int, nargs='+')
        parser.add_argument(name='--data', type=int, nargs='*')
        parser.add_argument(name='--name', type=str, nargs=1)

        output = parser.arg_parse(['--data'])
        self.assertEqual(output, '{"data": null}')

        output = parser.arg_parse(['--data', '12', '52', '89', '1', '--integers', '-1', '23'])
        self.assertEqual(output, '{"data": [12, 52, 89, 1], "integers": [-1, 23]}')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--name', 'abcd', 'xyz'])
        self.assertEqual(str(context.exception), 'Error : --name expects exactly 1 arguments but 2 arguments are found.')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--integers'])
        self.assertEqual(str(context.exception), 'Error : 1 or more arguments for the option --integers are required.')

    def test_repeat_and_default_values(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--name', type=str, repeat=True)  # default nargs='*'
        parser.add_argument(name='--strings')  # default type=str And repeat=False And nargs='*'

        output = parser.arg_parse(['--name', 'abcd', '--name', 'efgh', '--name', 'ijkl'])
        self.assertEqual(output, '{"name": ["abcd", "efgh", "ijkl"]}')

        output = parser.arg_parse(['--name', 'abcd', '--strings', '--name', 'efgh'])
        self.assertEqual(output, '{"name": ["abcd", "efgh"], "strings": null}')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--name', 'A', '--strings', '--name', 'B', '--strings', 'C'])
        self.assertEqual(str(context.exception), 'Error : --strings is not allowed to repeat.')

    def test_mutually_exclusive_group(self):
        # One mutually exclusive group
        parser = argparser.ArgumentParser()
        parser.add_mutually_exclusive_group(['--local', '--remote'])
        parser.add_argument(name='--key')
        parser.add_argument(name='--local')
        parser.add_argument(name='--remote')

        output = parser.arg_parse(['--local', 'a.b.c.d'])
        self.assertEqual(output, '{"local": "a.b.c.d"}')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--local', 'a.b.c.d', '--remote'])
        self.assertEqual(str(context.exception), "Error : ['--local', '--remote'] cannot appear together.")

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--key'])
        self.assertEqual(str(context.exception), "Error : Atleast one option among ['--local', '--remote'] is expected.")

        # Two mutually exclusive groups
        parser.add_mutually_exclusive_group(['--url', '--ip'])
        parser.add_argument(name='--url', nargs=1)
        parser.add_argument(name='--ip', nargs=1)

        output = parser.arg_parse(['--key', 'value', '--local', 'a.b.c.d', '--url', 'www.xyz.com'])
        self.assertEqual(output, '{"key": "value", "local": "a.b.c.d", "url": "www.xyz.com"}')

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--key', 'value', '--local', 'a.b.c.d', '--url', 'www.xyz.com', '--ip', '1.1.1.1'])
        self.assertEqual(str(context.exception), "Error : ['--url', '--ip'] cannot appear together.")

        with self.assertRaises(argparser.ParsingError) as context:
            parser.arg_parse(['--key', '--local'])
        self.assertEqual(str(context.exception), "Error : Atleast one option among ['--url', '--ip'] is expected.")

    def mul(self, args: Vector) -> int:
        res = 1
        for i in args:
            res *= i
        return res

    def test_action(self):
        parser = argparser.ArgumentParser()
        parser.add_argument(name='--sum', action=sum, nargs='+', type=int)
        parser.add_argument(name='--max', action=max, nargs='+', type=int)
        parser.add_argument(name='--mul', action=self.mul, nargs=3, type=int)   # Custom Action

        output = parser.arg_parse(['--sum', '1', '2', '3', '--max', '4', '6', '7', '12', '--mul', '2', '1', '3'])
        self.assertEqual(output, '{"sum": 6, "max": 12, "mul": 6}')

    def test_help(self):
        parser = argparser.ArgumentParser('Testing newly added features')
        parser.add_argument(name='--sum', action=sum, nargs='+', type=int, help="Finding sum", metavar='N')
        output = parser.print_help()
        self.assertEqual(output,
                         '{"description": "Testing newly added features", "usage": "[--help] [--sum [N [N...]]]", "optional arguments": ["--help show help message ", "--sum [N [N...]] Finding sum"]}')
        parser.add_argument(name='--max', action=max, nargs='+', type=int, help="Finding max", metavar='X')
        parser.add_argument(name='--foo', nargs=3, type=int, help="Testing default metavar")
        output = parser.arg_parse(['--help'])
        self.assertEqual(output,
                         '{"description": "Testing newly added features", "usage": "[--help] [--sum [N [N...]]] [--max [X [X...]]] [--foo FOO FOO FOO]", "optional arguments": ["--help show help message ", "--sum [N [N...]] Finding sum", "--max [X [X...]] Finding max", "--foo FOO FOO FOO Testing default metavar"]}')


if __name__ == '__main__':
    unittest.main()

# import argparser
# parser = argparser.ArgumentParser()
# parser.add_mutually_exclusive_group(['--local', '--remote'])
# parser.add_argument(name='--local', nargs=1)
# parser.add_argument(name='--remote')
# parser.add_argument(name='--x')
# parser.add_argument(name='--y')
# parser.add_argument(name='--z')
# parser.add_mutually_exclusive_group(['--x', '--y'])
# output = parser.arg_parse(['--local', '192.168.112.65', '--x', 'XXX', '--z', 'YYY'])
# print(output)
