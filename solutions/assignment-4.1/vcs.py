import argparse
import sys
import datetime
import Object
import Init
import Commit
import Diff
import Status
import Reset
import Checkout
import typing


class VCSError(Exception):
    """docstring for VCSError"""

    def __init__(self, message: str):
        super(VCSError, self).__init__(message)


class VCS(object):

    def __init__(self):
        parser = argparse.ArgumentParser(prog='vcs',
                                         description='Version Control System',
                                         usage='''vcs <command>

The most commonly used git commands are:
    init        Initialize .vcs repository in the active directory
    commit      Record changes to the repository
    diff        Find differences in the working directory to the given commit (default HEAD commit)
    log         Show all the commits
    status      Show the modified, deteled and untracked files since the last commit
    reset       Discard all changes since the last commit.
    checkout    Load the specified commit
''')
        parser.add_argument('command', type=str, help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])
        getattr(self, args.command, parser.print_help)()

    def init(self):
        parser = argparse.ArgumentParser(description='Initialize vcs in the working directory, no optional arguments required')
        parser.parse_args(sys.argv[2:])
        init_obj = Init.init()
        print(init_obj.status)

    def commit(self):
        parser = argparse.ArgumentParser(description='Record for changes in the directory')
        parser.add_argument('-m', action='store', type=str, default='', dest='message', help='Short message representing the changes in the commit')
        args = parser.parse_args(sys.argv[2:])
        print(Commit.commit(args.message))

    def diff(self):
        parser = argparse.ArgumentParser(description='Find the differences in the woking directory by comparing it to a given commit')
        head_hash = Object.get_HEAD()
        if head_hash is not None:
            head_hash = head_hash.get_hash()
        parser.add_argument('-c', action='store', default=head_hash, dest='commit_hash', help='Specifiles the commit hash, default is the HEAD commit')
        args = parser.parse_args(sys.argv[2:])
        if args.commit_hash is None:
            print('No commit exists')
            return
        commit_object = Object.commit(args.commit_hash)
        differences = Diff.diff(commit_object)
        if len(differences.files_modified) == 0:
            print('No files Modified')
        else:
            print(f'{len(differences.files_modified)} files modified\n++{differences.insertions} --{differences.deletions}\n')
            print(differences.modification_log)
        if len(differences.files_untracked) > 0:
            untracked_files = f'Untracked files: '
            for filename in differences.files_untracked:
                untracked_files += f'{filename} '
            print(untracked_files)

    def status(self):
        parser = argparse.ArgumentParser(description='Get the status of the working directory, no optional arguments required')
        parser.parse_args(sys.argv[2:])
        if Object.get_HEAD() is None:
            print('No Commit exists')
            return
        status_object = Status.status()
        if not status_object.any_modification_exists():
            print('Clean working directory\nNothing to commit')
            return
        print(status_object.get_files_modified())
        print(status_object.get_files_deleted())
        print(status_object.get_files_untracked())

    def log(self):
        parser = argparse.ArgumentParser(description='Print the log of commits of the working directory, no optional arguments required')
        parser.parse_args(sys.argv[2:])
        head = Object.get_HEAD()
        while head:
            print(f'\ncommit {head.get_hash()}')
            date_created = datetime.datetime.fromtimestamp(float(head.get_timestamp()))
            print(f'Date:\t{date_created.strftime("%c")}')
            print(f'\t{head.get_message()}')
            head = head.get_parent()

    def reset(self):  # Discard all changes since the last commit
        parser = argparse.ArgumentParser(description='Reset the changes in the woking directory to a given commit')
        head_hash = Object.get_HEAD()
        if head_hash is None:
            print('No commit exists')
            return
        head_hash = head_hash.get_hash()
        parser.add_argument('-c', action='store', default=head_hash, dest='commit_hash', help='Specifiles the commit hash, default is the HEAD commit')
        mutex = parser.add_mutually_exclusive_group()
        mutex.add_argument('-soft', action='store_true', help='Restores changes in the files modified. Keeps untracked and deleted files unchanged')
        mutex.add_argument('-hard', action='store_true', help='Restores all the changes. The working directory looks like the commit mentioned')

        args = parser.parse_args(sys.argv[2:])
        Reset.reset(Object.commit(args.commit_hash), args.soft, args.hard)

    def checkout(self):
        parser = argparse.ArgumentParser(description='Load the specified commit')
        if Object.get_HEAD() is None:
            print('No commit exists')
            return
        parser.add_argument('commit_hash', action='store', help='Specifiles the commit hash, default is the HEAD commit')
        args = parser.parse_args(sys.argv[2:])
        checkout = Checkout.checkout(old_commit=Object.get_HEAD(), new_commit=Object.commit(args.commit_hash))
        print(checkout.make_changes())


if __name__ == '__main__':
    VCS()
