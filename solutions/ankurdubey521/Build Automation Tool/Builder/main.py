from Builder.lib.commandrunner import run
from Builder.lib.buildconfig import BuildConfig, Command

import sys
import os


class Builder:
    def __init__(self):
        self.unresolved_commands = set()

    def _build_rule_handler(self, command_name, command_dir_abs, root_dir_abs, dry_run=False):
        """Parses JSON, Resolves Dependencies and Executes Command/Do a dry run"""

        # Remove Trailing '/' from paths if present
        if command_dir_abs.endswith('/'):
            command_dir_abs = command_dir_abs[:-1]
        if root_dir_abs.endswith('/'):
            root_dir_abs = root_dir_abs[:-1]

        # Mark the command's dependencies as unresolved
        self.unresolved_commands.add((command_name, command_dir_abs))

        # Parse build.json in current directory
        config = BuildConfig(command_dir_abs)
        command = config.get_command(command_name)

        # Process Dependencies
        try:
            deps = command.get_dependencies()
            if not dry_run:
                print("Executing {} dependencies for {} in {}...".format(len(deps), command_name, command_dir_abs))
            for dep in deps:
                dep_dir_abs = ''
                dep_name = ''
                if dep.startswith('//'):
                    # Command path referenced from root directory
                    dep_dir_abs = root_dir_abs + '/' + dep[2:]
                    dep_dir_abs, dep_name = dep_dir_abs.rsplit('/', 1)
                elif '/' in dep:
                    # Command in child directory
                    dep_dir_abs, dep_name = dep.rsplit('/', 1)
                    dep_dir_abs = command_dir_abs + "/" + dep_dir_abs
                else:
                    # Command in same directory
                    dep_name = dep
                    dep_dir_abs = command_dir_abs

                # Check for circular dependencies
                if (dep_name, dep_dir_abs) in self.unresolved_commands:
                    raise self.CircularDependencyException(
                        "Detected a Circular Dependency between {}:{} and {}:{}"
                        .format(dep_dir_abs, dep_name, command_dir_abs, command_name))

                self._build_rule_handler(dep_name, dep_dir_abs, root_dir_abs, dry_run)

        except Command.NoDependenciesException:
            print("No dependencies found for {} in {}...".format(command_name, command_dir_abs))

        # Mark the command's dependencies as resolved
        self.unresolved_commands.remove((command_name, command_dir_abs))

        if not dry_run:
            # Execute Command after processing dependencies
            print("Executing {} in {}".format(command_name, command_dir_abs))
            return_value = run(command.get_command_string(), command_dir_abs, print_command=True)

            # Stop Execution if Command Fails
            if return_value != 0:
                exit(-1)

    def execute_build_rule(self, command_name, command_dir_abs, root_dir_abs):
        # Do a dry run and check for syntax, do validation and check for circular dependencies
        self._build_rule_handler(command_name, command_dir_abs, root_dir_abs, dry_run=True)

        # If everything is fine do an actual run
        self._build_rule_handler(command_name, command_dir_abs, root_dir_abs)

    class CircularDependencyException(Exception):
        pass


if __name__ == '__main__':
    command = sys.argv[1]
    builder = Builder()
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = os.getcwd() + "/" + relative_path
    Builder.execute_build_rule(command, path, os.getcwd())
