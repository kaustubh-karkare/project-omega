import sys


class optional_arg_exception(Exception):

    def __init__(self, message):
        self.message = message

    def print_exception_msg():
        print('Optional Argument Error: ' + self.message)


class arguments_error(Exception):

    def __init__(self, message):
        self.message = message

    def print_exception_msg():
        print('Argument Error: ' + self.message)


class parser():

    def __init__(self):
        # positional arguments *necessary arguments*
        self.positional_arguments = []
        # optional arguments like --help
        self.optional_arguments = [{'name': '--help', 'shortname': '-h',
                                    'arg_type': 'string', 'required': False,
                                    'help': 'prints this help statement'}]
        # arguments that can't be used together
        self.mutually_exclusive_group = []
        self.mutually_exclusive_group_shortname = []
        # help statement
        self.usage_statement = ""
        self.help_statement = ""

    # add positional necessary arguments
    def add_argument(self, name, help='', arg_type='string'):
        self.positional_arguments.append(
            {'name': name, 'help': help, 'arg_type': arg_type})

    # add optional arguments
    def add_optional_arguments(self, name, shortname='', help="",
                               arg_type='string', required=False):
        if "--" not in name:
            raise optional_arg_exception("'--' missing for optional_arguments")
        else:
            self.optional_arguments.append(
                {'name': name, 'shortname': shortname, 'help': help, 'arg_type':
                 arg_type, 'required': required})

    # find index of dictionary from key value pair
    def find_index(self, dicts, key, value):
        class Null:
            pass
        for i, d in enumerate(dicts):
            if d.get(key, Null) == value:
                return i
        else:
            raise ValueError('no dict with the key and value combination found')

    def add_to_group(self, *args):
        list_of_grouped_arguments = []
        list_of_grouped_arguments_shortname = []
        for x in args:
            if "--" not in x:
                raise optional_arg_exception(
                    "'--' missing for optional_arguments")
            else:
                n = self.optional_arguments[self.find_index(
                    self.optional_arguments, 'name', x)]['shortname']
                list_of_grouped_arguments_shortname.append(n)
                list_of_grouped_arguments.append(x)
        self.mutually_exclusive_group.append(list_of_grouped_arguments)
        self.mutually_exclusive_group_shortname.append(
            list_of_grouped_arguments_shortname)

    def parse(self, argv):
        # generating help statement
        self.usage_statement = argv[0]
        for each in self.positional_arguments:
            h = each['name'] + '            ' + each['help'] + '\n'
            self.help_statement += h
            h = ' <' + each['name'] + '>'
            self.usage_statement += h
        for each in self.optional_arguments:
            h = each['name'] + '/' + each['shortname'] + \
                '              ' + each['help'] + '\n'
            self.help_statement += h
            h = ' [' + each['name'] + '/' + each['shortname'] + ']'
            self.usage_statement += h

        # checking for no. of positional ie. mandatory arguments and checking
        # for --help/-h option and extracting key value pair
        count_of_arguments = 0
        local_argument = {}
        local_optional_argument = {}
        for argument in argv[1:]:
            if '--' not in argument and '-' not in argument:
                count_of_arguments += 1
                local_argument[self.positional_arguments[
                    count_of_arguments - 1]['name']] = argument
            if argument == "--help" or argument == "-h":  # if argument has -h
                                                        # or --help in it
                print(self.usage_statement + "\n\n" + self.help_statement)
                exit()
            if '--' in argument and '=' in argument:
                x = argument.split('=')
                if (self.optional_arguments[self.find_index(
                        self.optional_arguments, 'name', x[0])]['shortname']
                        in local_optional_argument):
                    raise optional_arg_exception(
                        "used both long and shortname together")
                if x[0] not in local_optional_argument:
                    local_optional_argument[x[0]] = x[1]
                else:
                    raise optional_arg_exception(
                        "repeated usage of same argument")
            elif '-' in argument and '=' in argument:
                x = argument.split('=')
                if (self.optional_arguments[self.find_index(
                        self.optional_arguments, 'shortname', x[0])]['name']
                        in local_optional_argument):
                    raise optional_arg_exception(
                        "used both long and shortname together")
                if x[0] not in local_optional_argument:
                    local_optional_argument[x[0]] = x[1]
                else:
                    raise optional_arg_exception(
                        'repeated usage of same argument')
            if ('--' in argument or '-' in argument) and '=' not in argument:
                local_optional_argument[argument] = 'True'

        if len(self.positional_arguments) != count_of_arguments:
            raise arguments_error(
                "please enter valid positional arguments or use python3 " +
                argv[0] + " -h for help")

        # checking mutually exclusive arguments
        for list_of_grouped_arguments in self.mutually_exclusive_group:
            count_of_optional_arguments = 0
            for each in list_of_grouped_arguments:
                sn = self.optional_arguments[self.find_index(
                    self.optional_arguments, 'name', each)]['shortname']
                if (each in local_optional_argument
                        or sn in local_optional_argument):
                    count_of_optional_arguments += 1
                    if count_of_optional_arguments >= 2:
                        raise optional_arg_exception(
                            'mutually exclusive arguments used simultaneously' +
                            str(list_of_grouped_arguments))

        # checking for required arguments in optional_arguments and if boolean
        # is having some value other than true false
        for argument in self.optional_arguments:
            if (argument['required']
                and (argument['name']
                     not in local_optional_argument and argument['shortname']
                     not in local_optional_argument)):
                raise optional_arg_exception(
                    argument['name'] + ' is a required argument')
            if (argument['arg_type'] == 'string'
                    and argument['name'] in local_optional_argument
                    and local_optional_argument[argument['name']] == 'True'):
                raise optional_arg_exception(argument['name'] +
                                             " type error: string must be provided after = like -> "
                                             + argument['name'] + "=somevalue")
            if (argument['arg_type'] == 'string'
                    and argument['shortname'] in local_optional_argument
                    and local_optional_argument[argument['shortname']] == 'True'):
                raise optional_arg_exception(argument['shortname'] +
                                             " type error: string must be provided after = like -> "
                                             + argument['shortname'] + "=somevalue")
            if (argument['arg_type'] == 'boolean'
                    and argument['name'] in local_optional_argument
                    and local_optional_argument[argument['name']] != 'True'):
                raise optional_arg_exception(
                    argument['name'] + " type error: boolean can't have string")
            if (argument['arg_type'] == 'boolean'
                    and argument['shortname'] in local_optional_argument
                    and local_optional_argument[argument['shortname']] != 'True'):
                raise optional_arg_exception(
                    argument['name'] + " type error: boolean can't have string")
            if (argument['arg_type'] == 'number'
                    and argument['name'] in local_optional_argument):
                try:
                    int(local_optional_argument[argument['name']])
                except ValueError as e:
                    try:
                        float(local_optional_argument[argument['name']])
                    except ValueError as e:
                        raise optional_arg_exception(
                            'please eanter no for ' + argument['name'])
            if (argument['arg_type'] == 'number'
                    and argument['shortname'] in local_optional_argument):
                try:
                    int(local_optional_argument[argument['shortname']])
                except ValueError as e:
                    try:
                        float(local_optional_argument[argument['shortname']])
                    except ValueError as e:
                        raise optional_arg_exception(
                            'please eanter no for ' + argument['name'])

        final_json = {}
        name_list_of_arguments = []
        for each in self.positional_arguments:
            name_list_of_arguments.append(each['name'])
        for each in self.optional_arguments:
            name_list_of_arguments.append(each['name'])

        for each in local_argument:
            final_json[each] = local_argument[each]
        for each in local_optional_argument:
            if '--' in each:
                if each in name_list_of_arguments:
                    final_json[each[2:]] = local_optional_argument[each]
                else:
                    raise optional_arg_exception("used unknown option " + each)
            elif '-' in each:
                n = self.optional_arguments[self.find_index(
                    self.optional_arguments, 'shortname', each)]['name']
                if n in name_list_of_arguments:
                    final_json[n[2:]] = local_optional_argument[each]
                else:
                    raise optional_arg_exception("used unknown option " + each)

        return final_json


def Main():
    args = sys.argv
    parser1 = parser()
    parser1.add_argument('command', 'first positional argument')
    parser1.add_argument('subcommand', 'second positonal argument')
    parser1.add_optional_arguments(
        '--key', '-k', "key for whatever", 'number', True)
    parser1.add_optional_arguments('--name', '-n', 'name for whatever')
    parser1.add_optional_arguments(
        '--local', '-l', 'local thing whatever', 'boolean')
    parser1.add_optional_arguments(
        '--remote', '-r', 'remote thing whatever', 'boolean')
    parser1.add_optional_arguments(
        '--nat', '', 'remote thing whatever', 'boolean')
    parser1.add_optional_arguments(
        '--bridged', '-b', 'remote thing whatever', 'boolean')
    parser1.add_optional_arguments(
        '--host', '', 'remote thing whatever', 'boolean')
    parser1.add_to_group('--local', '--remote')
    parser1.add_to_group('--nat', '--bridged', '--host')
    x = parser1.parse(args)
    print(x)

if __name__ == '__main__':
    Main()
