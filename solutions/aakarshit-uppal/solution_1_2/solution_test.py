#!/usr/bin/env python3
"""Tests for solution module."""
import unittest
import solution


class TestArgAddition(unittest.TestCase):

    def setUp(self):
        self.parser = solution.Parser(test=True)

    def test_duplicate_addition(self):
        self.parser.add_arg('--first', setval=True)
        with self.assertRaises(solution.DuplicateArgError):
            self.parser.add_arg('--first', setval=True)


class TestArgParsing(unittest.TestCase):

    def setUp(self):
        self.parser = solution.Parser(test=True)
        self.parser.add_arg('command', type=str)

    def test_positional_args(self):
        self.parser.add_arg('subcommand', type=str)
        self.parser.parse('alpha beta')
        expected_values = {'command': 'alpha', 'subcommand': 'beta'}
        real_values = self.parser.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_short_name(self):
        self.parser.add_arg('--verbose', '-V', setval=True)
        real_values = self.parser.get_non_none_values()
        self.parser.parse('alpha -V')
        expected_values = {'command': 'alpha', 'verbose': True}
        real_values = self.parser.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_multiple_values(self):
        self.parser.add_arg('--dimen', type=int, nvals=2)
        self.parser.parse('area --dimen 12 10')
        expected_values = {'command': 'area', 'dimen': [12, 10]}
        real_values = self.parser.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_required_arg_not_used(self):
        self.parser.add_arg('--key', type=int, required=True)
        with self.assertRaises(solution.RequiredArgError):
            self.parser.parse('alpha beta')

    def test_multiple_exclusive_args_used(self):
        self.parser.add_arg('--none', setval=True)
        self.parser.add_arg('--single', setval=True)
        self.parser.add_arg('--many', setval=True)
        self.parser.make_args_exclusive('--none', '--single', '--many')
        with self.assertRaises(solution.ExclusiveArgError):
            self.parser.parse('--single --many')

    def test_too_few_values(self):
        self.parser.add_arg('--dimen', type=int, nvals=2)
        with self.assertRaises(solution.ValueCountError):
            self.parser.parse('area --dimen 12')

    def test_invalid_value_type(self):
        self.parser.add_arg('--len', type=int)
        with self.assertRaises(solution.ValueTypeError):
            self.parser.parse('area --len abc')

    def test_allowed_posargs_exceeded(self):
        with self.assertRaises(solution.PosargCountError):
            self.parser.parse('alpha beta gamma delta')

    def test_undefined_arg_used(self):
        with self.assertRaises(solution.UnknownArgError):
            self.parser.parse('alpha --real')

    def assertEqualDict(self, dict_a, dict_b):
        for key in dict_a:
            self.assertEqual(dict_a[key], dict_b[key])


if __name__ == '__main__':
    unittest.main()
