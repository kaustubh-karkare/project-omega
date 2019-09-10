from Builder.lib.commandrunner import run
from Builder.lib.buildconfig import BuildConfig, Command
import sys
import os


def execute(command_name, containing_folder_path):
    """Parses JSON, Resolves Dependencies and Executes Command"""

    # Parse build.json in current directory
    config = BuildConfig(containing_folder_path)
    command = config.get_command(command_name)

    # Parse Dependencies First
    try:
        deps = command.get_dependencies()
        dep_count = len(deps)
        print("Executing {} dependencies for {} in {}...".format(dep_count, command_name, containing_folder_path))
        for dep in deps:
            if '/' in dep:
                # Command in Child Folder
                dep_containing_folder_path, dep_command = dep.rsplit('/', 1)
                dep_containing_folder_path = containing_folder_path + "/" + dep_containing_folder_path
                execute(dep_command, dep_containing_folder_path)
            else:
                # Command in Same Folder
                execute(dep, containing_folder_path)
    except Command.NoDependenciesException:
        print("No dependencies found for {} in {}...".format(command_name, containing_folder_path))

    # Execute Command after processing dependencies
    print("Executing {} in {}".format(command_name, containing_folder_path))
    return_value = run(command.get_command_string(), containing_folder_path, print_command=True)

    # Stop Execution if Command Fails
    if return_value != 0:
        exit(-1)


if __name__ == '__main__':
    command = sys.argv[1]
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.getcwd() + "/" + relative_path
    execute(command, path)
