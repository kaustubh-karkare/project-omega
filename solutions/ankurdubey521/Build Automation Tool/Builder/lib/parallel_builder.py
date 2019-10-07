from Builder.lib.buildconfig import BuildRule, BuildConfig
from concurrent.futures import ProcessPoolExecutor
import subprocess


class ParallelBuilder:
    def __init__(self):
        pass

    class CircularDependencyException(Exception):
        pass

    @staticmethod
    def run_shell(self, command_string: str, cwd: str = '/', print_command: bool = False) -> int:
        """Run Command and Return Exit Code. Optionally Print the command itself"""
        if print_command:
            print(command_string)
        return subprocess.run(command_string, shell=True, cwd=cwd).returncode

