import ngc
import argparse
from os import getcwd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='+')
    parser.add_argument('--location', type=str, default=getcwd())
    args = parser.parse_args()

    ngc_obj = ngc.Ngc(repo_path=args.location)

    if args.command[0] == 'init':
        ngc_obj.init()
    elif args.command[0] == 'status':
        ngc_obj.status()
    elif args.command[0] ==  'commit':
        commit_message = input("Enter commit message: ")
        ngc_obj.commit(message=commit_message)
    elif args.command[0] == 'log':
        if len(args.command) == 1:
            ngc_obj.log()
        else:
            ngc_obj.log(commit_hash=args.command[1])
    elif args.command[0] == 'config_user':
        ngc_obj.config_user(user_name=args.command[1], user_email=args.command[2])
    elif args.command[0] == 'checkout':
        if len(args.command) > 1:
            ngc_obj.checkout(commit_hash=args.command[1])
        else:
            ngc_obj.checkout()
    elif args.command[0] == 'reset':
        ngc_obj.reset()
    else:
        print("Error: Command not recognized")
