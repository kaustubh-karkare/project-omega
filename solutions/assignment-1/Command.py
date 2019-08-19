import re


class Command(object):
    """Command contains the features related to particular command. It also has validators to validate conditions while parsing."""

    def __init__(self, name, usage, regex, type_allowed, no_of_arg, conflicting_commands, required_commands, overwrite):
        self.name = name  # Command name
        self.usage = usage  # What is the use of this command
        self.regex = r'^' + regex + r'$'  # Regular expression which can distinguish the correct type of argument
        self.type_allowed = type_allowed  # Type of arguments allowed for the command
        self.no_of_arg = no_of_arg  # Number of arguments required for the command
        self.conflicting_commands = conflicting_commands  # Commands which should not apprear together with self.name
        self.required_commands = required_commands  # Commands which should appear with self.name
        self.overwrite = overwrite  # Commands can appear multiple times

    def validate(self, result_space, args):
        self.validate_type(args)
        self.validate_conficting_commands(result_space)
        self.validate_overwrite(result_space)

    def validate_type(self, args):
        for i in args:
            if re.search(self.regex, i) is None:
                raise Exception(f'{i} is not {self.type_allowed}. A {self.type_allowed} type argument is expected')
        return True

    def validate_conficting_commands(self, result_space):
        if self.conflicting_commands:
            for i in self.conflicting_commands:
                if i in result_space:
                    raise Exception(f'\"{self.name}\" and \"--{i}\" cannot be used together.')
        return True

    def validate_required_commands(self, result_space):
        if self.required_commands:
            for i in self.required_commands:
                if i not in result_space:
                    raise Exception(f'\"{self.name}\" also requires \"{i}\" which is missing')
        return True

    def validate_overwrite(self, result_space):
        if self.name[2:] in result_space:
            if self.overwrite != True:
                raise Exception(f'\"{self.name}\" cannot appear more that once.')
        return True
