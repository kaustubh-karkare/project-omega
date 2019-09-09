import subprocess


def run(command_string, cwd, print_command):
    if print_command:
        print(command_string)
    return subprocess.run(command_string, shell=True, cwd=cwd).returncode


if __name__ == '__main__':
    pass
