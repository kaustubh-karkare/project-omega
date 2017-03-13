"""Module facilitating parsing of command line arguments.

Supports positional and optional arguments, and more features, like:
    - Arguments can be added with specific paramters:
        - alias (to add short name for argument)
        - required (to make argument compulsory)
        - type (to specify type of value for argument)
        - nvals (to specify number of values for argument)
        - set_value (to specify value to be set on argument use)
    - Multiple values can be passed for argument
    - Values passed on call can be accessed as ordered or simple dictionary in:
        - Long form (including none-valued)
        - Short form (excluding none-valued)
    - Values can be printed in JSON format

Usage Example::
    solution.add_arg('command', type=str)
    solution.add_arg('subcommand', type=str)
    solution.add_arg('--keys', type=int, nvals=2, required=True)
    solution.add_arg('--verbose', '-V', set_value=True)
    solution.add_arg('--local', set_value=True)
    solution.add_arg('--remote', set_value=True)
    solution.make_args_exclusive('--local', '--remote')
    solution.parse('alpha beta --keys 1 2 -V')
    solution.print_json()
Output::
    {"command": "alpha", "subcommand": "beta", "keys": [1, 2], "verbose": true}
"""
import sys as _sys  # For argv (to read arguments from command line)
import json as _json  # For dumps (to convert dict to JSON)
import collections as _collections  # For OrderedDict (For ordered values)

_arg_params = {}
_positional_args = []
_optional_args = []
_required_args = []
_exclusive_groups = []
_arg_values = _collections.OrderedDict()


def _get_new_params_list():
    # Returns initial params list
    return {'alias': None,
            'required': False,
            'type': None,
            'nvals': 1,
            'value': None,
            'set_value': None}


def _get_arg_params(arg_name):
    # Returns param list of arg_name (if existent)
    if arg_name in _arg_params:
        return _arg_params[arg_name]
    else:
        for arg in _arg_params:
            if _arg_params[arg]['alias'] == arg_name:
                return _arg_params[arg]
    _handle_error('no_such_arg', arg_name)


def _handle_error(type_of_error, *arg_names):
    # Handles all parsing related errors
    if type_of_error is 'duplicate_arg':
        print('Error: The argument', arg_names[0], 'already exists.')
    if type_of_error is 'missing_required':
        print('Error: The ', arg_names[0],
              'argument is required, but missing from input.')
    if type_of_error is 'exclusive':
        print('Error:', str(arg_names)[1:-1], 'cannot be used together.')
    if type_of_error is 'no_such_arg':
        print('Error: Invalid argument', arg_names[0])
    if type_of_error is 'too_few_values':
        print('Error: Too few values supplied for', arg_names[0])
    if type_of_error is 'invalid_type':
        print('Error: Invalid value type(s) for', arg_names[0])
    if type_of_error is 'too_many_posargs':
        print('Error: Too many positional arguments.')
    print_usage()
    _sys.exit(0)


def _check_required(cli_args):
    # Checks if all required arguments were used
    for arg in _required_args:
        if arg not in cli_args:
            _handle_error('missing_required', arg)


def _check_exclusive(cli_args):
    # Checks if two or more exclusive arguments were used
    for arg_group in _exclusive_groups:
        common_args = set.intersection(set(arg_group), set(cli_args))
        common_args = list(common_args)
        common_args.sort()
        if len(common_args) > 1:
            _handle_error('exclusive', *common_args)


def _check_and_assign_values(cli_args):
    # Checks values with params and assigns them
    i = 0
    positional_tracker = 0

    while i < len(cli_args):
        curr_arg = cli_args[i]

        if curr_arg[0] is '-':
            params = _get_arg_params(curr_arg)
            if params is None:
                return
            if params['nvals'] is 0:
                params['value'] = params['set_value']
            elif params['nvals'] is 1:
                i += 1
                try:
                    params['value'] = params['type'](cli_args[i])
                except IndexError:
                    _handle_error('too_few_values', curr_arg)
                except ValueError:
                    _handle_error('invalid_type', curr_arg)
            else:
                i += 1
                l = []
                for j in range(params['nvals']):
                    try:
                        l.append(params['type'](cli_args[i]))
                        i += 1
                    except IndexError:
                        _handle_error('too_few_values', curr_arg)
                    except ValueError:
                        _handle_error('invalid_type', curr_arg)
                i -= 1
                params['value'] = l
        else:
            try:
                curr_posarg = _positional_args[positional_tracker]
                posarg_params = _arg_params[curr_posarg]
                posarg_params['value'] = posarg_params['type'](curr_arg)
                positional_tracker += 1
            except IndexError:
                _handle_error('too_many_posargs')
            except ValueError:
                _handle_error('invalid_type', curr_posarg)
        i += 1
    _put_values()


def _put_values():
    # Populates _arg_values with argument names and corresponding values
    for arg in _positional_args:
        _arg_values[arg] = _arg_params[arg]['value']
    for arg in _optional_args:
        clean_arg = arg[2:]
        _arg_values[clean_arg] = _arg_params[arg]['value']


def add_arg(name, *alias, **params):
    """Add new argument.

    name -- name of argument
    alias -- alias/short name for argument
    params -- one or more of:
        required=(boolean)
        type=(python type)
        nvals=(number of values)
        set_value=(value to set)
    """
    if name in _positional_args or name in _optional_args:
        _handle_error('duplicate_arg', name)

    new_arg_params = _get_new_params_list()

    if len(alias):
        new_arg_params['alias'] = alias[0]
    for key in params:
        new_arg_params[key] = params[key]
    _arg_params[name] = new_arg_params

    if name[0] is '-':
        _optional_args.append(name)
    else:
        _positional_args.append(name)
    if new_arg_params['required'] is True:
        _required_args.append(name)
    if _arg_params[name]['set_value'] is not None:
        _arg_params[name]['nvals'] = 0
        _arg_params[name]['type'] = type(_arg_params[name]['set_value'])


def make_args_exclusive(*exclusive_args):
    """Make (already added) arguments exclusive.

    exclusive_args -- list of arguments to add to exclusive group
    """
    new_exclusive_group = tuple(exclusive_args)
    _exclusive_groups.append(new_exclusive_group)


def print_usage():
    """Print usage string."""
    usage = 'usage: '
    for arg in _positional_args:
        if not _arg_params[arg]['required']:
            usage += '['
        usage += arg
        if not _arg_params[arg]['required']:
            usage += ']'
        usage += ' '
    for arg in _optional_args:
        if not _arg_params[arg]['required']:
            usage += '['
        usage += arg
        if _arg_params[arg]['alias'] is not None:
            usage += '/' + _arg_params[arg]['alias']
        if _arg_params[arg]['nvals']:
            usage += '=' + str(_arg_params[arg]['type'])[8:-2]
        if not _arg_params[arg]['required']:
            usage += ']'
        usage += ' '
    print(usage)
    if len(_exclusive_groups):
        exclusives_list = 'exclusive groups: '
        for arg_group in _exclusive_groups:
            exclusives_list += str(arg_group) + ' '
        print(exclusives_list)


def parse(*cli_args):
    """Parse command line arguments.

    cli_args -- string containing arguments to parse
    """
    if not len(cli_args):
        cli_args = _sys.argv
        cli_args.remove(cli_args[0])
    else:
        cli_args = cli_args[0].split()
    for i in range(len(cli_args)):
        cli_args[i] = cli_args[i].split('=')
    cli_args = sum(cli_args, [])

    _check_required(cli_args)
    _check_exclusive(cli_args)
    _check_and_assign_values(cli_args)


def get_values():
    """Return dictionary containing values of arguments."""
    return dict(_arg_values)


def get_ordered_values():
    """Return ordered dictionary containing values of arguments."""
    return _collections.OrderedDict(_arg_values)


def get_non_none_values():
    """Return dictionary containing non-none values of arguments."""
    non_none_values = dict(_arg_values)
    for arg in _arg_values:
        if _arg_values[arg] is None:
            del non_none_values[arg]
    return dict(non_none_values)


def get_ordered_non_none_values():
    """Return ordered dictionary containing non-none values of arguments."""
    non_none_values = _collections.OrderedDict(_arg_values)
    for arg in _arg_values:
        if _arg_values[arg] is None:
            del non_none_values[arg]
    return _collections.OrderedDict(non_none_values)


def print_json():
    """Print non-none values in JSON format."""
    non_none_values = get_ordered_non_none_values()
    arg_json = _json.dumps(non_none_values)
    print(arg_json)
