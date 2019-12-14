import vcs_files
import os
import hashlib
from typing import Dict, Optional, Union


def get_HEAD() -> Optional[commit]:
    with open(vcs_files.HEAD, 'r') as headfile:
        head_pointer = headfile.read()
        if head_pointer == '':
            return None
        elif head_pointer.startswith('ref: '):
            with open(head_pointer.split()[1], 'r') as head_file:
                head_pointer = head_file.read()
        return commit(head_pointer)


def set_HEAD(commit_hash: str) -> None:
    with open(vcs_files.HEAD, 'w') as headfile:
        headfile.write(commit_hash)


# class branch(object):

#     def __init__(self):
#         pass


class commit(object):

    def __init__(self, commit_hash: Optional[str]=None):
        self.object_type: str = 'commit'
        self.parent: Optional[commit] = None
        self.tree_obj: Optional[tree] = None
        self.message: str = ''
        self.timestamp: str = ''
        if commit_hash:
            self.set_hash(commit_hash)

    def save_object(self) -> None:
        with open(os.path.join(vcs_files.OBJECTS, self.get_hash()), 'w') as commit_file:
            commit_file.write(self.get_content())

    def set_hash(self, hash: str) -> None:
        with open(os.path.join(vcs_files.OBJECTS, hash), 'r') as commit_file:
            parent_hash = commit_file.readline().split()[1]
            if parent_hash != 'None':
                self.parent = commit(parent_hash)
            tree_hash = commit_file.readline().split()[1]
            self.tree_obj = tree(tree_hash)
            self.message = commit_file.readline().split('"')[1]
            self.timestamp = commit_file.readline().split()[1]

    def set_tree(self, tree_obj: tree) -> None:
        self.tree_obj = tree_obj

    def set_parent(self, parent: commit) -> None:
        self.parent = parent

    def set_message(self, message: str) -> None:
        self.message = message

    def set_timestamp(self, timestamp: str) -> None:
        self.timestamp = timestamp

    def get_hash(self) -> str:
        content = self.get_content()
        hash_value = hashlib.sha1(content.encode(encoding='utf-8')).hexdigest()
        return hash_value

    def get_tree(self) -> Optional[tree]:
        return self.tree_obj

    def get_parent(self) -> Optional[commit]:
        return self.parent

    def get_message(self) -> str:
        return self.message

    def get_timestamp(self) -> str:
        return self.timestamp

    def get_content(self) -> str:
        content = ''
        if self.parent:
            content += f'parent {self.parent.get_hash()}\n'
        else:
            content += f'parent None\n'
        content += f'tree {self.tree_obj.get_hash()}\n'
        content += f'message "{self.message}"\n'
        content += f'timestamp {self.timestamp}'
        return content


class tree(object):

    def __init__(self, tree_hash: Optional[str]=None):
        self.object_type: str = 'tree'
        self.blobs: Dict[str, blob] = dict()
        self.trees: Dict[str, tree] = dict()
        if tree_hash:
            self.set_hash(tree_hash)

    def set_hash(self, tree_hash: str) -> None:
        with open(os.path.join(vcs_files.OBJECTS, tree_hash), 'r') as tree_file:
            line = tree_file.readline()
            while line:
                [object_type, object_hash, object_name] = line.split()
                if object_type == 'blob':
                    self.blobs[object_name] = blob(object_hash)
                else:
                    self.trees[object_name] = tree(object_hash)
                line = tree_file.readline()

    def save_object(self) -> None:
        tree_path = os.path.join(vcs_files.OBJECTS, self.get_hash())
        if os.path.exists(tree_path):
            return
        with open(tree_path, 'w') as tree_file:
            tree_file.write(self.get_content())

    def add_object(self, file_object, filename: str) -> None:
        if file_object.object_type == 'tree':
            self.trees[filename] = file_object
        if file_object.object_type == 'blob':
            self.blobs[filename] = file_object

    def get_hash(self) -> str:
        content = self.get_content()
        hash_value = hashlib.sha1(content.encode(encoding='utf-8')).hexdigest()
        return hash_value

    def get_content(self) -> str:
        content = ''
        for filename in self.trees:
            content += f'tree {self.trees[filename].get_hash()} {filename}\n'
        for filename in self.blobs:
            content += f'blob {self.blobs[filename].get_hash()} {filename}\n'
        return content


class blob(object):

    def __init__(self, blob_hash: str=None):
        self.object_type: str = 'blob'
        self.content: str = ''
        if blob_hash:
            self.set_hash(blob_hash)

    def set_hash(self, blob_hash) -> None:
        with open(os.path.join(vcs_files.OBJECTS, blob_hash), 'r') as blob_file:
            self.content = blob_file.read()

    def save_object(self) -> None:
        blob_path = os.path.join(vcs_files.OBJECTS, self.get_hash())
        if os.path.exists(blob_path):
            return
        with open(os.path.join(vcs_files.OBJECTS, self.get_hash()), 'w') as blob_file:
            blob_file.write(self.content)

    def get_content(self) -> str:
        return self.content

    def get_hash(self) -> str:
        hash_value = hashlib.sha1(self.content.encode(encoding='utf-8')).hexdigest()
        return hash_value

    def set_content(self, content) -> None:
        self.content = content

    def set_content_from_file(self, filepath) -> None:
        with open(filepath, 'r') as read_file:
            self.content = read_file.read()
