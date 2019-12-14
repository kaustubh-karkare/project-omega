import Diff
import shutil
import os


class reset(object):
    """docstring for reset"""

    def __init__(self, commit, soft, hard):
        differences = Diff.diff(commit)
        if soft or hard:
            for filepath in differences.files_modified:
                with open(filepath, 'w') as reset_file:
                    reset_file.write(differences.files_modified[filepath].get_content())

        if hard:
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
