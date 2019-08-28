import json
from typing import Any, List


class ParsingError(Exception):
    """Generates custom exception related to argparse module only"""

    def __init__(self, message):
        super().__init__(f'Error : {message}.')


class Option(object):
    """Option contains the features related to a particular option"""

    def __init__(self, name: str, action: Any, nargs: Any, type: Any, repeat: bool):
        super(Option, self).__init__()
        self.name = name.split('--')[-1]
        if action is None:
            self.action = self.store
        else:
            self.action = action
        if nargs is None:
            self.nargs = '*'
        else:
            self.nargs = nargs
        if type is None:
            self.type = str
        else:
            self.type = type
        if repeat is None:
            self.repeat = False
        else:
            self.repeat = True
        self.clear()

    def clear(self) -> None:
        self.count = 0
        self.args = []

    def insert_arg(self, arg: str) -> None:
        arg = self.validate_type(arg)
        self.args.append(arg)

    def validate_repeat(self) -> None:
        if self.repeat is False:
            if self.count == 1:
                raise ParsingError(f'--{self.name} is not allowed to repeat')
        self.count += 1

    def validate_type(self, arg: str) -> None:
        try:
            arg = self.type(arg)
            return arg
        except ValueError as e:
            raise ParsingError(f'Invalid type of argument "{arg}", {e}')

    def validate_nargs(self) -> None:
        if self.nargs == '*':
            return
        elif self.nargs == '+':
            if len(self.args) == 0:
                raise ParsingError(f'1 or more arguments for the option --{self.name} are required')
        elif self.nargs == '?':
            if len(self.args) > 1:
                raise ParsingError(f'Extra arguments for the option --{self.name} are found')
        else:
            if self.nargs is not len(self.args):
                raise ParsingError(f'--{self.name} expects exactly {self.nargs} arguments but {len(self.args)} arguments are found')

    def output(self) -> dict:
        self.validate_nargs()
        return {self.name: self.action(self.args)}

    def store(self, args: List)-> (int, List):  # Store is the default action to be taken by an option
        if len(args) == 1:
            return args[0]
        elif len(args) == 0:
            return None
        return args


class ArgumentParser(object):
    """ArgumentParser creates a set of valid command line options. Command line arguments can be parsed against this ArgumentParser"""

    def __init__(self, description=None, usage=None):
        super(ArgumentParser, self).__init__()
        self.is_mutually_exclusive_group = False
        self.options = {}

    def add_argument(self, name: str, action=None, nargs=None, type=None, repeat=None):
        if name in self.options:
            raise ParsingError(f'Multiple defination of an argument is not allowed')
        else:
            self.options[name] = Option(name, action, nargs, type, repeat)

    def add_mutually_exclusive_group(self) -> None:
        self.is_mutually_exclusive_group = True

    def validate_mutually_exclusive_group(self, arg_parse_options: List[Option]) -> None:
        if self.is_mutually_exclusive_group:
            if len(arg_parse_options) > 1:
                conflicting_options = []
                for element in arg_parse_options:
                    conflicting_options.append(element.name)
                raise ParsingError(f'{conflicting_options} options cannot appear together')
            if len(arg_parse_options) == 0:
                raise ParsingError(f'Atleast one option is required')

    def arg_parse(self, args: List)-> (str, ParsingError):
        try:
            arg_parse_options = []
            output = {}
            for element in self.options:
                self.options[element].clear()

            option = None
            for arg in args:
                if arg in self.options:
                    option = self.options[arg]
                    if option.count == 0:
                        arg_parse_options.append(option)
                    option.validate_repeat()
                else:
                    if option is None:
                        raise ParsingError(f'Invalid argument {arg} detected')
                    else:
                        option.insert_arg(arg)

            self.validate_mutually_exclusive_group(arg_parse_options)

            for element in arg_parse_options:
                output.update(element.output())
            return json.dumps(output)
        except ParsingError as parsingError:
            return parsingError
