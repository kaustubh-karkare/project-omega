import sys
import json

COMMANDS = {}
"""COMMANDS contains the list of all available commands"""

KEY_COMMAND = {
    'command_name': '--key',
    'command_type': 'positive integer'
}

NAME_COMMAND = {
    'command_name': '--name',
    'command_type': 'albhapets only',
    'required_command': KEY_COMMAND
}

LOCAL_COMMAND = {
    'command_name': '--local',
}

REMOTE_COMMAND = {
    'command_name': '--remote',
    'conflicting_with': LOCAL_COMMAND
}

COMMANDS['--key'] = KEY_COMMAND
COMMANDS['--name'] = NAME_COMMAND
COMMANDS['--local'] = LOCAL_COMMAND
COMMANDS['--remote'] = REMOTE_COMMAND


def validate_key(key_value):  # to validate the argument provided to --key command
    try:
        key_value = int(key_value)
    except Exception:
        return -1
    return 1


def validate_name(name_value):  # to validate the argument provided to --name command
    if name_value.isalpha():
        return 1
    return -1


def main(argv):
    results = {}
    commands_found = []
    error_message = None
    for arg in argv[1:]:
        argument = arg.split('=')
        command = argument[0]
        commands_found.append(command)
        if command in ('--local', '--remote'):
            if command == '--local':
                results['--local'] = True
            elif command == '--remote':
                results['--remote'] = False
            continue
        if command not in COMMANDS:
            error_message = command + ' is not a recognized command'
        else:
            if len(argument) > 2:
                error_message = 'invalid number of arguments passed to ' + command
            elif len(argument) < 2:
                error_message = 'too few arguments to ' + command
            elif len(argument) == 2:
                value = argument[1]
                if command == '--key':
                    check_key = validate_key(value)
                    if check_key == -1:
                        error_message = 'invalid argument to ' + command
                    else:
                        results['--key'] = value
                elif command == '--name':
                    check_name = validate_name(value)
                    if check_name == -1:
                        error_message = 'invalid argument to ' + command
                    else:
                        results['--name'] = value
        if error_message:
            break

    if error_message is not None:
        """some error occurred"""
    elif '--local' in commands_found and '--remote' in commands_found:
        error_message = 'The "--local" and "--remote" arguments cannot be used together'
    elif '--key' not in commands_found and '--local' not in commands_found and '--remote' not in commands_found:
        error_message = 'The \'--key\' argument is required, but missing from input'

    final_response = error_message
    if error_message is None:
        final_response = json.dumps(results, sort_keys=True)
    print(final_response)
    return final_response


if __name__ == '__main__':
    main(sys.argv)
