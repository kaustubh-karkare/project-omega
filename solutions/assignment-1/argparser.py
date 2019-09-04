import json
from typing import Any, List, Dict, Union


class ParsingError(Exception):
    """Generates custom exception related to argparse module only"""

    def __init__(self, message: str):
        super().__init__(f'Error : {message}.')

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


class Option(object):
    """Option contains the features related to a particular option"""

    def __init__(self, name: str, action: Any, nargs: Union[int, str], type: Any, repeat: bool, help: str, metavar: Union[None, str]):
        super(Option, self).__init__()
        assert name.startswith('--')
        self.name = name
        self.action = action
        self.nargs = nargs
        self.type = type
        self.repeat = repeat
        self.help = help
        if metavar is None:
            self.metavar = (self.name.split("--")[1]).upper()
        else:
            self.metavar = metavar
        self.generate_usage()

    def generate_usage(self) -> None:
        usage: str = self.name
        if type(self.nargs) is int:
            for i in range(0, self.nargs):
                usage += f' {self.metavar}'
        elif self.nargs == '?':
            usage += f' [{self.metavar}]'
        elif self.nargs == '+':
            usage += f' {self.metavar} [{self.metavar}...]'
        elif self.nargs == '*':
            usage += f' [{self.metavar} [{self.metavar}...]]'
        self.usage = usage

    def validate_repeat(self) -> None:
        if self.repeat is False:
            raise ParsingError(f'{self.name} is not allowed to repeat')

    def validate_type(self, arg: str) -> Any:
        try:
            arg = self.type(arg)
            return arg
        except ValueError as e:
            raise ParsingError(f'Invalid type of argument "{arg}", {e}')

    def validate_nargs(self, len_args: int) -> None:
        if self.nargs == '*':
            return
        elif self.nargs == '+':
            if len_args == 0:
                raise ParsingError(f'1 or more arguments for the option {self.name} are required')
        elif self.nargs == '?':
            if len_args > 1:
                raise ParsingError(f'Extra arguments for the option {self.name} are found')
        else:
            if self.nargs is not len_args:
                raise ParsingError(f'{self.name} expects exactly {self.nargs} arguments but {len_args} arguments are found')

    def output(self, args: List[Any]) -> Dict[str, Any]:
        option_name = self.name.split('--')[1]
        return {option_name: self.action(args)}

    @staticmethod
    def store(args: List[Any])-> Any:  # Store is the default action to be taken by an option
        if len(args) == 1:
            return args[0]
        elif len(args) == 0:
            return None
        return args


class ArgumentParser(object):
    """ArgumentParser creates a set of valid command line options. Command line arguments can be parsed against this ArgumentParser"""

    def __init__(self, description: str=None):
        super(ArgumentParser, self).__init__()
        self.description = description
        self.mutually_exclusive_group: Dict[str, str] = {}  # It contains a dictionary of mutually exclusive options in the form {option: identifier}, identifier is used to identify the group of mutually exclusive options i.e if 2 options have same identifier then they are mutually exclusive
        self.mutually_exclusive_group_identifier: List[str] = []   # It stores all the possible identifiers, this will be used to find all the mutually exclusive groups
        self.options: Dict[str, Option] = {}  # Whenever an argument is added using add_argument() then the object Option created is stored in this dictionary in the form {name: Option}

    def add_argument(self, name: str, action: Any=Option.store, nargs: Union[int, str]='*', type: Any =str, repeat: bool=False, help: str='No description provided', metavar: Union[None, str]=None) -> None:
        if name in self.options:
            raise ParsingError(f'Multiple defination of an argument is not allowed')
        else:
            self.options[name] = Option(name, action, nargs, type, repeat, help, metavar)

    def add_mutually_exclusive_group(self, group: List[str]) -> None:
        if len(group) > 0:
            identifier = group[0]
            for option in group:
                if option in self.mutually_exclusive_group:
                    raise ParsingError(f'{option} cannot be added in two different mutually exclusive groups')
                else:
                    self.mutually_exclusive_group[option] = identifier
            if identifier not in self.mutually_exclusive_group_identifier:
                self.mutually_exclusive_group_identifier.append(identifier)

    def validate_mutually_exclusive_group(self, arg_parse_mutex_group: Dict[str, List[str]]) -> None:
        for identifier in self.mutually_exclusive_group_identifier:
            if len(arg_parse_mutex_group[identifier]) > 1:
                raise ParsingError(f'{arg_parse_mutex_group[identifier]} cannot appear together')
            elif len(arg_parse_mutex_group[identifier]) == 0:
                mutex_list = []
                for option in self.mutually_exclusive_group:
                    if self.mutually_exclusive_group[option] == identifier:
                        mutex_list.append(option)
                raise ParsingError(f'Atleast one option among {mutex_list} is expected')

    def validate_option(self, argument: str, arg_parse_options: dict, arg_parse_mutex_group: dict) -> Option:
        if argument in self.mutually_exclusive_group:
            identifier = self.mutually_exclusive_group[argument]
            (arg_parse_mutex_group[identifier]).append(argument)

        if argument in arg_parse_options:
            self.options[argument].validate_repeat()
        else:
            arg_parse_options[argument] = []
        return self.options[argument]

    def insert_value(self, option: Option, value: str, arg_parse_options: dict)-> None:
        value = option.validate_type(value)
        (arg_parse_options[option.name]).append(value)

    def arg_parse(self, arguments: List[str]) -> str:

        if len(arguments) == 1 and (arguments[0] == '--help'):
            return self.print_help()

        arg_parse_mutex_group: Dict[str, List[str]] = {}  # It is used to store the options of a mutually exclusive group together in the form {identifier: List[str]}, the size of the List[str] should always be 1 to be valid
        arg_parse_options: Dict[str, List[Any]] = {}  # It stores the options which occur as arguments to be parsed
        output: Dict[str, Any] = {}

        for identifier in self.mutually_exclusive_group_identifier:
            arg_parse_mutex_group[identifier] = []

        option = None
        for arg in arguments:
            if arg in self.options:     # arg represents an Option
                option = self.validate_option(arg, arg_parse_options, arg_parse_mutex_group)
            else:                       # arg represents a value
                if option is None:
                    raise ParsingError(f'Invalid argument {arg} detected')
                else:
                    self.insert_value(option, arg, arg_parse_options)

        self.validate_mutually_exclusive_group(arg_parse_mutex_group)

        for arg in arg_parse_options:
            self.options[arg].validate_nargs(len(arg_parse_options[arg]))
            output.update(self.options[arg].output(arg_parse_options[arg]))

        return json.dumps(output)

    def print_help(self) -> str:
        output: Dict[str, Any] = {}
        output['description'] = self.description
        optional_arguments = ['--help show help message ']
        usage = '[--help]'
        for option in self.options:
            optional_arguments.append(f'{self.options[option].usage} {self.options[option].help}')
            usage += f' [{self.options[option].usage}]'
        output['usage'] = usage
        output['optional arguments'] = optional_arguments
        return json.dumps(output)
