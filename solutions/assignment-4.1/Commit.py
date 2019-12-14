import Object
import Status
import os
import datetime
import vcs_files
from typing import Union


class commit(object):
    """docstring for commit"""

    def __init__(self, message=''):
        self.status = None
        if Object.get_HEAD() is not None:
            if Status.status().any_modification_exists() is False:
                self.status = 'Clean working directory\nNothing to commit'
                return
        commit_object = Object.commit()
        commit_object.set_parent(Object.get_HEAD())
        tree_object = self._save_object(os.getcwd())
        commit_object.set_tree(tree_object)
        commit_object.set_message(message)
        commit_object.set_timestamp(datetime.datetime.today().timestamp())
        commit_object.save_object()
        Object.set_HEAD(commit_object.get_hash())
        return

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
