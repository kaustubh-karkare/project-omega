from Builder.lib.commandrunner import run
from Builder.lib.buildconfig import BuildConfig
import sys
import os


def execute(command, containing_folder_path):
    """Parses JSON, Resolves Dependencies and Executes Command"""

    # Parse build.json in current directory
    config = BuildConfig(containing_folder_path + "/build.json")

    # Parse Dependencies First
    try:
        deps = config.deps(command)
        dep_count = len(deps)
        print("Executing {} dependencies for {} in {}...".format(dep_count, command, containing_folder_path))
        for dep in deps:
            try:
                # Command in Child Folder
                dep_containing_folder_path, dep_command = dep.rsplit('/', 1)
                dep_containing_folder_path = containing_folder_path + "/" + dep_containing_folder_path
                execute(dep_command, dep_containing_folder_path)
            except ValueError:
                # Command in Same Folder
                execute(dep, containing_folder_path)
    except KeyError:
        # No Dependencies
        print("No dependencies found for {} in {}...".format(command, containing_folder_path))

    # Execute Command after processing dependencies
    print("Executing {} in {}".format(command, containing_folder_path))
    return_value = run(config.command(command), containing_folder_path, print_command=True)

    # Stop Execution if Command Fails
    if return_value != 0:
        exit(-1)


if __name__ == '__main__':
    command = sys.argv[1]
    execute(command, os.getcwd())
