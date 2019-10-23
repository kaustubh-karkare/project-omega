import enum
import json
import os
import subprocess
import sys


class Build(object):
    """
    The class builds the dependencies, checks for the existence of required
    files and executes the build command for the specified name.
    """

    class BuildSpecs(enum.Enum):
        BUILD = 'build.json'
        NAME = 'name'
        DEPENDENCIES = 'dependencies'
        FILES = 'files'
        COMMAND = 'command'

    def __init__(self, build_file=os.path.join(os.getcwd(), 'build.json')):
        """
        :param build_file: Path of the build file.
        :type build_file: str
        """

        self.build_instructions = None
        with open(build_file, 'r') as build_file:
            self.build_instructions = json.load(build_file)

    def _getBuildInstruction(self, name):
        """
        Returns the build instruction available for name.

        :param name: The name of the build instruction.
        :type name: str
        """

        for build_instruction in self.build_instructions:
            if build_instruction[self.BuildSpecs.NAME.value] == name:
                return build_instruction
        return None

    def _buildDependencies(self, dependencies):
        """
        Builds the dependencies for the current build instruction.

        :param dependencies: The dependecnies to build.
        :type depenedecies: list
        """

        for dependency in dependencies:
            build_directory, name = os.path.split(dependency)
            if build_directory:
                current_directory = os.getcwd()
                try:
                    os.chdir(build_directory)
                    build_dependency = Build(
                        os.path.join(os.getcwd(), self.BuildSpecs.BUILD.value))
                    build_dependency.build(name)
                finally:
                    os.chdir(current_directory)
            else:
                build_dependency = Build(
                    os.path.join(os.getcwd(), self.BuildSpecs.BUILD.value))
                build_dependency.build(name)

    def _ensureFiles(self, files):
        """
        Asserts if all the files are exists or not

        :param files: Files to check for existence
        :type files: list
        """

        for file in files:
            assert os.path.isfile(file)

    def _executeCommand(self, command):
        """
        Executes the command.

        :param command: Command to execute
        :type command: str
        """

        completed_process = subprocess.run(
            command,
            shell=True,
            check=True,
            universal_newlines=True,
        )
        return completed_process.returncode

    def build(self, name):
        build_instruction = self._getBuildInstruction(name)
        if build_instruction is None:
            raise NameError(f'No build instruction for "{name}".')

        self._buildDependencies(
            build_instruction.get(self.BuildSpecs.DEPENDENCIES.value, []))
        self._ensureFiles(
            build_instruction.get(self.BuildSpecs.FILES.value, []))
        self._executeCommand(
            build_instruction.get(self.BuildSpecs.COMMAND.value, ""))


def main():
    if len(sys.argv) <= 1:
        sys.stdout.write("No build name given.")
        sys.exit(0)
    build = Build()
    try:
        build.build(name=sys.argv[1])
    except NameError as e:
        sys.stdout.write(str(e))


if __name__ == '__main__':
    main()
