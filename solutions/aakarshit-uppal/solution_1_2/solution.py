"""Module facilitating parsing of command line arguments.

Salient features:
    - Supports positional and optional arguments
    - Arguments can be added with specific attributes:
        - alias (to add short name for argument)
        - required (to make argument compulsory)
        - type (to specify type of value for argument)
        - nvals (to specify number of values for argument)
        - setval (to specify value to be set on argument use)
    - Values passed on call can be accessed as a dictionary in:
        - Long form (all arguments)
        - Short form (excluding arguments with none value)
    - Usage string can be printed, showing value types, count etc.
    - Values can be printed in JSON format

Usage Example::
    parser = solution.Parser()
    parser.add_arg('command', type=str)
    parser.add_arg('subcommand', type=str)
    parser.add_arg('--keys', type=int, nvals=2, required=True)
    parser.add_arg('--verbose', '-V', setval=True)
    parser.add_arg('--local', setval=True)
    parser.add_arg('--remote', setval=True)
    parser.make_args_exclusive('--local', '--remote')
    parser.parse('alpha beta --keys 1 2 -V')
    solution.print_json(parser)
Output::
    {"command": "alpha", "subcommand": "beta", "keys": [1, 2], "verbose": true}
"""
import sys as _sys  # For argv (to read arguments from command line)
import json as _json  # For dumps (to convert dict to JSON)
import collections as _collections  # For OrderedDict (For ordered values)
from solution_exceptions import *  # For Exceptions


class _Argument:
    # Defines attributes for arguments.
    def __init__(self, alias,
                 required=False,
                 type=None,
                 nvals=1,
                 setval=None):
        self.alias = alias
        self.required = required
        self.type_ = type
        self.nvals = nvals
        self.setval = setval
        if self.setval is not None:
            self.nvals = 0
            self.type_ = __builtins__['type'](self.setval)
        self.value = None
        self.excl_tuple = -1


class Parser:
    """Parses arguments."""

    def __init__(self):
        """Initialize lists and dictionaries."""
        self._args = {}
        self._positional_args = []
        self._optional_args = []
        self._required_args = []
        self._exclusive_groups = []
        self._arg_values = _collections.OrderedDict()

    def _get_arg(self, arg_name):
        # Returns _Argument object corresponding to arg_name (if existent)
        if arg_name in self._args:
            return self._args[arg_name]
        else:
            for arg in self._args:
                if self._args[arg].alias == arg_name:
                    return self._args[arg]
        raise UnknownArgError(arg_name)

    def _ensure_required(self, cli_args):
        # Checks if all required arguments were used
        for arg in self._required_args:
            if arg not in cli_args and self._args[arg].alias not in cli_args:
                raise RequiredArgError(arg)

    def _ensure_exclusive(self, cli_args):
        # Checks if two or more exclusive arguments were used
        for arg_group in self._exclusive_groups:
            common_args = set.intersection(set(arg_group), set(cli_args))
            if len(common_args) > 1:
                raise ExclusiveArgError(common_args)

    def _ensure_and_assign_values(self, cli_args):
        # Checks values with argument attributes and assigns them
        i = 0
        positional_tracker = 0

        while i < len(cli_args):
            curr_arg = cli_args[i]

            if curr_arg[0] is '-':
                arg = self._get_arg(curr_arg)
                if arg.nvals is 0:
                    arg.value = arg.setval
                else:
                    try:
                        vals = []
                        for _ in range(arg.nvals):
                            i += 1
                            vals.append(arg.type_(cli_args[i]))
                        if arg.nvals is 1:
                            vals = vals[0]
                        arg.value = vals
                    except IndexError:
                        raise ValueCountError(curr_arg)
                    except ValueError:
                        raise ValueTypeError(curr_arg)
            else:
                try:
                    curr_posarg = self._positional_args[positional_tracker]
                    posarg = self._args[curr_posarg]
                    posarg.value = posarg.type_(curr_arg)
                    positional_tracker += 1
                except IndexError:
                    raise PosargCountError()
                except ValueError:
                    raise PosargTypeError(curr_posarg)
            i += 1
        self._put_values()

    def _put_values(self):
        # Populates self._arg_values with argument names and corresponding
        # values
        for posarg_name in self._positional_args:
            self._arg_values[posarg_name] = self._args[posarg_name].value
        for optarg_name in self._optional_args:
            clean_arg_name = optarg_name[2:]
            self._arg_values[clean_arg_name] = self._args[optarg_name].value

    def add_arg(self, name, alias=None, **attributes):
        """Add new argument.

        name -- name of argument
        alias -- alias/short name for argument
        attributes -- one or more of:
            required=(boolean)
            type=(python type)
            nvals=(number of values)
            setval=(value to set)
        """
        if name in self._positional_args or name in self._optional_args:
            raise DuplicateArgError(name)

        new_arg = _Argument(alias, **attributes)

        if name[0] is '-':
            self._optional_args.append(name)
        else:
            self._positional_args.append(name)
        if new_arg.required is True:
            self._required_args.append(name)
        self._args[name] = new_arg

    def make_args_exclusive(self, *exclusive_args):
        """Make (already added) arguments exclusive.

        exclusive_args -- list of argument names to add to exclusive group
        """
        exclusive_tuple_index = len(self._exclusive_groups)
        for arg_name in exclusive_args:
            self._args[arg_name].excl_tuple = exclusive_tuple_index
        new_exclusive_group = tuple(exclusive_args)
        self._exclusive_groups.append(new_exclusive_group)

    def print_usage(self):
        """Print usage string."""
        usage = 'usage: '

        # Handle posargs
        for posarg_name in self._positional_args:
            posarg = self._args[posarg_name]
            if not posarg.required:
                usage += '['
            usage += posarg_name
            if not posarg.required:
                usage += ']'
            usage += ' '

        # Handle optargs
        excl_optargs_to_skip = []
        for optarg_name in self._optional_args:

            # Prevent duplication of exclusive optargs
            if optarg_name in excl_optargs_to_skip:
                continue

            optarg = self._args[optarg_name]
            if not optarg.required:
                usage += '['
            usage += optarg_name

            # Handle alias
            if optarg.alias is not None:
                usage += '/' + optarg.alias

            # Handle exclusive optargs
            exclusive_tuple_index = optarg.excl_tuple
            if exclusive_tuple_index is not -1:
                excl_args = self._exclusive_groups[exclusive_tuple_index]
                other_excl_args = [x for x in excl_args if x != optarg_name]
                for arg_name in other_excl_args:
                    usage += '|' + arg_name
                    if self._args[arg_name].alias is not None:
                        usage += '/' + self._args[arg_name].alias
                    excl_optargs_to_skip.append(arg_name)

            # Handle optargs having nval > 0
            no_of_values = optarg.nvals
            if no_of_values:
                while no_of_values:
                    usage += ' ' + str(optarg.type_)[8:-2]
                    no_of_values -= 1

            if not optarg.required:
                usage += ']'
            usage += ' '

        print(usage)

    def parse(self, cli_args=str(_sys.argv)[1:-1]):
        """Parse command line arguments.

        cli_args -- string containing arguments to parse
        """
        if cli_args is not _sys.argv:
            cli_args = cli_args.split()
        for i in range(len(cli_args)):
            cli_args[i] = cli_args[i].split('=')
        cli_args = sum(cli_args, [])

        self._ensure_required(cli_args)
        self._ensure_exclusive(cli_args)
        self._ensure_and_assign_values(cli_args)

    def get_values(self):
        """Return dictionary containing values of arguments."""
        return dict(self._arg_values)

    def get_non_none_values(self):
        """Return dictionary containing args with non-none values."""
        non_none_values = dict(self._arg_values)
        for arg in self._arg_values:
            if self._arg_values[arg] is None:
                del non_none_values[arg]
        return dict(non_none_values)


def print_json(parser):
    """Print non-none values in JSON format."""
    non_none_values = _collections.OrderedDict(parser._arg_values)
    for arg in parser._arg_values:
        if parser._arg_values[arg] is None:
            del non_none_values[arg]
    arg_json = _json.dumps(non_none_values)
    print(arg_json)
