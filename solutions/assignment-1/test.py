import v2
import json

parser = v2.Parser()
parser.add_argument('key', int, required=True)
parser.add_argument('name', str)
parser.add_argument('local', None, cant_be_used_with=['remote'])
parser.add_argument('remote', None, cant_be_used_with=['local'])
parser.parse_arguments()
args = parser.args
output_dict = dict()
for arg in args:
    if args[arg].used:
        output_dict[arg] = args[arg].value

print(json.dumps(output_dict))

