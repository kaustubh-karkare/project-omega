import Object
import Diff
import os
import shutil
from typing import Set, Dict, Union


class checkout(object):
    def __init__(self, old_commit, new_commit):
        self.old_obj = old_commit
        self.new_obj = new_commit
        self.common_files: Set[str] = set()
        self.files_to_be_deleted: Set[str] = set()
        self.modified_files: Dict[str, Object.blob] = dict()
        self.files_to_be_added: Dict[str, Union[Object.tree, Object.blob]] = dict()
        self.diff = Diff.diff(self.old_obj)
        self.commit_commit_compare('.', self.old_obj.get_tree(), self.new_obj.get_tree())

    def commit_commit_compare(self, filepath: str, old_obj, new_obj):
        if old_obj.get_hash() == new_obj.get_hash():
            self.common_files.add(filepath)
            return
        elif old_obj.object_type == 'blob':
            self.modified_files[filepath] = new_obj
            return

        for filename in old_obj.trees:
            if filename in new_obj.trees:
                self.commit_commit_compare(os.path.join(filepath, filename), old_obj.trees[filename], new_obj.trees[filename])
            else:
                self.files_to_be_deleted.add(os.path.join(filepath, filename))

        for filename in old_obj.blobs:
            if filename in new_obj.blobs:
                self.commit_commit_compare(os.path.join(filepath, filename), old_obj.blobs[filename], new_obj.blobs[filename])
            else:
                self.files_to_be_deleted.add(os.path.join(filepath, filename))

        for filename in new_obj.trees:
            if filename not in old_obj.trees:
                self.files_to_be_added[os.path.join(filepath, filename)] = new_obj.trees[filename]

        for filename in new_obj.blobs:
            if filename not in old_obj.blobs:
                self.files_to_be_added[os.path.join(filepath, filename)] = new_obj.blobs[filename]

    def make_changes(self):
        # First check if the chekout is possible completely. If not possible abort the process else continue.
        for filename in self.modified_files:
            if not self.is_modifiable(filename):
                return f'Aborting checkout\nUnsaved changes detected\n{filename} is modified and needs to be committed before checkout'
        for filename in self.files_to_be_deleted:
            if not self.is_deletable(filename):
                return f'Aborting checkout\nUnsaved changes detected\n{filename} is modified and needs to be committed before checkout'
        for filename in self.files_to_be_added:
            if not self.is_addable(filename):
                return f'Aborting checkout\nUnsaved changes detected\n{filename} is untracked and needs to be committed before checkout'

        self.modify_files()
        self.delete_files()
        self.add_files()
        Object.set_HEAD(self.new_obj.get_hash())
        return f'Updated head : {self.new_obj.get_hash()}'

    def is_modifiable(self, filepath):  # Checking for some unsaved changes
        if filepath in self.diff.files_modified:
            return False
        if not os.path.exists(filepath):
            return False
        return True

    def is_deletable(self, filepath):
        if filepath in self.diff.files_deleted:
            return False
        if filepath in self.diff.files_modified:
            return False
        if filepath in self.diff.files_untracked:
            return False
        if not os.path.isdir(filepath):
            return True
        for filename in os.listdir(filepath):
            if not self.is_deletable(os.path.join(filepath, filename)):
                return False
        return True

    def is_addable(self, filename):
        if os.path.exists(filename):
            return False
        return True

    def modify_files(self):
        for filename in self.modified_files:
            with open(filename, 'w') as write_file:
                write_file.write(self.modified_files[filename].get_content())

    def delete_files(self):
        for filename in self.files_to_be_deleted:
            try:
                shutil.rmtree(filename)
            except NotADirectoryError:
                os.remove(filename)

    def add_files(self):
        for filename in self.files_to_be_added:
            self.recreate_tree(filename, self.files_to_be_added[filename])

    def recreate_tree(self, filepath, vcs_object):
        if vcs_object.object_type == 'tree':
            os.mkdir(filepath)
            for filename in vcs_object.trees:
                self.recreate_tree(os.path.join(filepath, filename), vcs_object.trees[filename])
            for filename in vcs_object.blobs:
                self.recreate_tree(os.path.join(filepath, filename), vcs_object.blobs[filename])
            return
        with open(filepath, 'w') as blob_file:
            blob_file.write(vcs_object.get_content())
