from Command import Command
import sys
import json

commands = {}  # Contains the list of allowed commands
"""Inserting Commands"""
"""Command is of the type (command_name, command_description, regex_allowed, type_allowed, no_of_arg, conflicting_commands, required_commands, can_overwrite)"""
commands['--key'] = Command('--key', 'Stores key value pair', r'\+?\d+', "positive integer", 1, None, None, False)
commands['--name'] = Command('--name', 'Defines name', r'[a-zA-Z]+', 'alphabetic', 1, None, ['key'], True)
commands['--local'] = Command('--local', 'Defines id of local machine', r'\w+', 'word', 1, ['remote'], None, False)
commands['--remote'] = Command('--remote', 'Defines id of remote machine', r'\w+', 'word', 1, ['local'], None, False)


error_message = None
result_space = {}

for arg in sys.argv[1:]:
    arg_list = arg.split('=')
    cmd = arg_list[0]    # cmd is the command name

    if cmd not in commands:
        error_message = f'{cmd} is an invalid command'
    else:
        if commands[cmd].no_of_arg == 1:
            if len(arg_list) > 2:
                error_message = f'{arg} has invalid syntax'
            elif len(arg_list) < 2:
                error_message = f'{arg} needs one argument which is missing'
            else:
                try:
                    commands[cmd].validate(result_space, arg_list[1:])
                    result_space[cmd[2:]] = arg_list[1]
                except Exception as e:
                    error_message = e
    if error_message:
        break

if not error_message:
    for i in result_space:
        try:
            commands['--' + i].validate_required_commands(result_space)
        except Exception as e:
            error_message = e

if error_message:
    print(f'Error : {error_message}')
else:
    print(json.dumps(result_space))
