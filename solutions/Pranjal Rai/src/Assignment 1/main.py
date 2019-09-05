import CommandLineParser as CLP
import TestCommandLParser as TEST
import sys

KEY_COMMAND = CLP.AddCommand('--key', 'positive integer', r'\d+', None, None, False)
NAME_COMMAND = CLP.AddCommand('--name', 'albhapets only', r'[a-zA-Z]+', '--key', None, False)
LOCAL_COMMAND = CLP.AddCommand('--local', None, r'/\A\z/', None, '--remote', True)
REMOTE_COMMAND = CLP.AddCommand('--remote', None, r'/\A\z/', None, '--local', True)

if __name__ == '__main__':
    CLP.CommandLineParser().get_arguments(sys.argv)
    TEST.TestCommandLParser().call_functions()