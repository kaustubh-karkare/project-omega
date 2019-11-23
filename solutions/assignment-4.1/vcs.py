import argparse
import os
import hashlib
import sys
import datetime
import vcs_files
import Object
import Diff
import Status
import Checkout
import shutil
from typing import Union

class VCS(object):

    def __init__(self):
        parser = argparse.ArgumentParser(prog='vcs',
                                         description='Version Control System',
                                         usage='''vcs <command>

The most commonly used git commands are:
    init        Intitialize .vcs repository in the active directory
    commit      Record changes to the repository
    diff        Find differences in the working directory to the given commit (default HEAD commit)
    log         Show all the commits
    status      Show the modified, deteled and untracked files since the last commit
''')
        parser.add_argument('command', type=str, help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])
        getattr(self, args.command, parser.print_help)()

    def init(self):
        FILE_STRUCTURE = {
            vcs_files.ROOT: 'dir',
            vcs_files.OBJECTS: 'dir',
            vcs_files.REFS: 'dir',
            vcs_files.MASTER: 'file',
            vcs_files.HEAD: 'file'
        }
        if os.path.exists(vcs_files.ROOT):
            print('Reinitializing vcs in this directory')
            return
        for filename in FILE_STRUCTURE:
            if FILE_STRUCTURE[filename] == 'dir':
                try:
                    os.makedirs(os.path.realpath(filename))
                except WindowsError:
                    pass
                continue
            try:
                os.makedirs(os.path.dirname(os.path.realpath(filename)))
            except WindowsError:
                pass
            finally:
                with open(filename, 'w') as newfile:
                    newfile.write('')
        print('Initializing vcs in this directory')

    def commit(self):
        parser = argparse.ArgumentParser(description='Record for changes in the directory')
        parser.add_argument('-m', type=str, default='', help='Short message representing the changes in the commit')
        args = parser.parse_args(sys.argv[2:])
        if Object.get_HEAD() is not None:
            if Status.status().any_modification_exists() is False:
                print('Clean working directory\nNothing to commit')
                return
        commit_object = Object.commit()
        commit_object.set_parent(Object.get_HEAD())
        tree_object = self._save_object(os.getcwd())
        commit_object.set_tree(tree_object)
        commit_object.set_message(args.m)
        commit_object.set_timestamp(datetime.datetime.today().timestamp())
        commit_object.save_object()
        Object.set_HEAD(commit_object.get_hash())

    def _save_object(self, active_path: str) -> Union[Object.blob, Object.tree]:
        if os.path.isdir(active_path):
            tree_object = Object.tree()
            for filename in os.listdir(active_path):
                if filename == vcs_files.ROOT:
                    continue
                filepath = os.path.join(active_path, filename)
                vcs_object = self._save_object(filepath)
                tree_object.add_object(vcs_object, filename)
            tree_object.save_object()
            return tree_object
        blob_object = Object.blob()
        blob_object.set_content_from_file(active_path)
        blob_object.save_object()
        return blob_object

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
        if len(differences.files_modified)==0:
            print('No files Modified')
        else:
            print(f'{len(differences.files_modified)} files modified\n++{differences.insertions} --{differences.deletions}\n')
            print(differences.modification_log)
        if len(differences.files_untracked)>0:
            untracked_files = f'Untracked files: '
            for filename in differences.files_untracked:
                untracked_files += f'{filename} '
            print(untracked_files)

    def status(self):
        if Object.get_HEAD() is None:
            print('No Commit exists')
            return
        status_object = Status.status()
        if not status_object.any_modification_exists():
            print('Clean working directory\nNothing to commit')
            return
        print(status_object.get_modified_files())
        print(status_object.get_deleted_files())
        print(status_object.get_untracked_files())

    def log(self):
        head = Object.get_HEAD()
        while head:
            print(f'\ncommit {head.get_hash()}')
            date_created = datetime.datetime.fromtimestamp(float(head.get_timestamp()))
            print(f'Date:\t{date_created.strftime("%c")}')
            print(f'\t{head.get_message()}')
            head = head.get_parent()

    def reset(self):    #Discard all changes since the last commit
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
        differences = Diff.diff(Object.commit(args.commit_hash))
        for filepath in differences.files_modified:
            with open(filepath, 'w') as reset_file:
                reset_file.write(differences.files_modified[filepath].get_content())

        if args.hard:
            for filepath in differences.files_untracked:
                try:
                    shutil.rmtree(os.path.realpath(filepath))
                except NotADirectoryError:
                    os.remove(os.path.realpath(filepath))

            for filepath in differences.files_deleted:
                self._reset_tree(filepath, differences.files_deleted[filepath])

    def _reset_tree(self, filepath, vcs_object):
        if vcs_object.object_type == 'tree':
            os.mkdir(filepath)
            for dirname in vcs_object.trees:
                self._reset_tree(os.path.join(filepath, dirname), vcs_object.trees[dirname])
            for filename in vcs_object.blobs:
                self._reset_tree(os.path.join(filepath, filename), vcs_object.blobs[filename])
            return
        with open(filepath, 'w') as reset_file:
            reset_file.write(vcs_object.get_content())

    def checkout(self):
        parser = argparse.ArgumentParser(description='Load the specified commit')
        if Object.get_HEAD() is None:
            print('No commit exists')
            return
        parser.add_argument('commit_hash', action='store', help='Specifiles the commit hash, default is the HEAD commit')
        args = parser.parse_args(sys.argv[2:])
        checkout = Checkout.checkout(Object.get_HEAD(), Object.commit(args.commit_hash))
        print(checkout.make_changes())


if __name__ == '__main__':
    VCS()
