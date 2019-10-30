import cliparser
import sys
cliparser.add_option('--key', int, True)
cliparser.add_option('--name', str, True)
cliparser.add_option('--age', int, False)
cliparser.add_option('--local', bool, False, '--remote')
cliparser.add_option('--remote', bool, False, '--local')
input_from_command_line=sys.argv
cliparser.parse(input_from_command_line)
