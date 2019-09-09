from Builder.lib.commandrunner import run
from Builder.lib.buildconfig import BuildConfig
import sys
import os


def execute(command, containing_folder_path):
    config = BuildConfig(containing_folder_path + "/build.json")
    try:
        deps = config.deps(command)
        dep_count = len(deps)
        print("Executing {} dependencies for {} in {}...".format(dep_count, command, containing_folder_path))
        for dep in deps:
            try:
                dep_containing_folder_path, dep_command = dep.rsplit('/', 1)
                dep_containing_folder_path = os.getcwd() + "/" + dep_containing_folder_path
                execute(dep_command, dep_containing_folder_path)
            except ValueError:
                execute(dep, containing_folder_path)
    except KeyError:
        print("No dependencies found for {} in {}...".format(command, containing_folder_path))
    print("Executing {} in {}".format(command, containing_folder_path))
    run(config.command(command), containing_folder_path, print_command=True)


if __name__ == '__main__':
    command = sys.argv[1]
    execute(command, os.getcwd())