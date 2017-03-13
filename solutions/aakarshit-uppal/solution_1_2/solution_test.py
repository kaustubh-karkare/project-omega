#!/usr/bin/env python3
"""Tests for solution module."""
import unittest
import unittest.mock
import solution


class TestAddition(unittest.TestCase):

    def test_duplicate_addition(self):
        solution.add_arg('--first', set_value=True)
        solution._handle_error = unittest.mock.Mock()
        solution.add_arg('--first', set_value=True)
        solution._handle_error.assert_called_once_with(
            'duplicate_arg', '--first')


class TestParsing(unittest.TestCase):

    def setUp(self):
        solution.add_arg('command', type=str)
        solution.add_arg('subcommand', type=str)

    def test_positional_args(self):
        solution.parse('alpha beta')
        expected_values = {'command': 'alpha', 'subcommand': 'beta'}
        real_values = solution.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_short_name(self):
        solution.add_arg('--verbose', '-V', set_value=True)
        solution.parse('alpha -V')
        expected_values = {'command': 'alpha', 'verbose': True}
        real_values = solution.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_multiple_values(self):
        solution.add_arg('--dimen', type=int, nvals=2)
        solution.parse('area --dimen 12 10')
        expected_values = {'command': 'area', 'dimen': [12, 10]}
        real_values = solution.get_non_none_values()
        self.assertEqualDict(expected_values, real_values)

    def test_required_arg_not_used(self):
        solution.add_arg('--key', type=int, required=True)
        solution._handle_error = unittest.mock.Mock()
        solution.parse('alpha beta')
        solution._handle_error.assert_called_with('missing_required', '--key')

    def test_multiple_exclusive_args_used(self):
        solution.add_arg('--none', set_value=True)
        solution.add_arg('--single', set_value=True)
        solution.add_arg('--many', set_value=True)
        solution.make_args_exclusive('--none', '--single', '--many')
        solution._handle_error = unittest.mock.Mock()
        solution.parse('--single --many')
        solution._handle_error.assert_called_with('exclusive',
                                                  '--many',
                                                  '--single')

    def test_too_few_values(self):
        solution.add_arg('--dimen', type=int, nvals=2)
        solution._handle_error = unittest.mock.Mock()
        solution.parse('area --dimen 12')
        solution._handle_error.assert_called_with('too_few_values', '--dimen')

    def test_invalid_value_type(self):
        solution.add_arg('--len', type=int)
        solution._handle_error = unittest.mock.Mock()
        solution.parse('area --len abc')
        solution._handle_error.assert_called_with('invalid_type', '--len')

    def test_allowed_posargs_exceeded(self):
        solution._handle_error = unittest.mock.Mock()
        solution.parse('alpha beta gamma delta')
        solution._handle_error.assert_called_with('too_many_posargs')

    def test_undefined_arg_used(self):
        solution._handle_error = unittest.mock.Mock()
        solution.parse('alpha --real')
        solution._handle_error.assert_called_with('no_such_arg', '--real')

    def assertEqualDict(self, dict_a, dict_b):
        for key in dict_a:
            self.assertEqual(dict_a[key], dict_b[key])


if __name__ == '__main__':
    unittest.main()
