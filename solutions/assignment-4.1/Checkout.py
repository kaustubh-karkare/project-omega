import Object
import Diff
import os, shutil

class checkout(object):
    def __init__(self, commit_object_a, commit_object_b ):
        self.commit_object_a = commit_object_a
        self.commit_object_b = commit_object_b
        self.common_files = set()
        self.files_to_be_deleted = set()
        self.modified_files = dict()
        self.files_to_be_added = dict()
        self.diff = Diff.diff(self.commit_object_a)
        self.commit_commit_compare('.', commit_object_a.get_tree(), commit_object_b.get_tree())


    def commit_commit_compare(self, filepath: str, a, b):
        # print(f'filepath: {filepath} , {a.object_type} , {b.object_type}, {a.get_hash()}, {b.get_hash()}')
        if a.get_hash() == b.get_hash():
            self.common_files.add(filepath)
            return
        elif a.object_type == 'blob':
            self.modified_files[filepath] = b
            return

        for filename in a.trees:
            if filename in b.trees:
                self.commit_commit_compare(os.path.join(filepath, filename), a.trees[filename], b.trees[filename])
            else:
                self.files_to_be_deleted.add(os.path.join(filepath, filename))

        for filename in a.blobs:
            if filename in b.blobs:
                self.commit_commit_compare(os.path.join(filepath, filename), a.blobs[filename], b.blobs[filename])
            else:
                self.files_to_be_deleted.add(os.path.join(filepath, filename))

        for filename in b.trees:
            if not filename in a.trees:
                self.files_to_be_added[os.path.join(filepath, filename)] = b.trees[filename]

        for filename in b.blobs:
            if not filename in a.blobs:
                self.files_to_be_added[os.path.join(filepath, filename)] = b.blobs[filename]

    def make_changes(self):
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
        Object.set_HEAD(self.commit_object_b.get_hash())
        return f'Updated head : {self.commit_object_b.get_hash()}'

    def is_modifiable(self, filepath):
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
            if not self.is_deletable(os.path.join(filepath,filename)):
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
