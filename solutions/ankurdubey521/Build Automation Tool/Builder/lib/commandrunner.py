import subprocess


def run(command_string):
    return subprocess.run(command_string, shell=True).returncode


if __name__ == '__main__':
    pass
