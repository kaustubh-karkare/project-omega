import main
import sys
if __name__ == '__main__':
    printer = main.assignment1()
    ans = printer.createoptions(
        key=(1234, "r", "local"), name=("shivam", "nr", "local"))
    commands = sys.argv[1:]
    printer.parsecommands(commands)

