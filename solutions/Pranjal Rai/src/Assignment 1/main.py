import CommandLineParser as CLP
import sys


if __name__ == '__main__':
	commands = {}
	new_command = CLP.AddCommand
	new_command('--key', 'positive integer', r'\d+', None, None, False, commands)
	new_command('--name', 'albhapets only', r'[a-zA-Z]+', '--key', None, False, commands)
	new_command('--local', None, r'/\A\z/', None, '--remote', True, commands)
	new_command('--remote', None, r'/\A\z/', None, '--local', True, commands)
	parser = CLP.CommandLineParser(commands)
	parser.get_arguments(sys.argv)
