import subprocess


def run(command_string, cwd, print_command=False):
    """Run Command and Return Exit Code. Optionally Print the command itself"""
    if print_command:
        print(command_string)
    return subprocess.run(command_string, shell=True, cwd=cwd).returncode

