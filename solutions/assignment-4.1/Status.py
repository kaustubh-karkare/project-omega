import Diff
import Object


class status(object):
    def __init__(self):
        self.diff_object = Diff.diff(Object.get_HEAD())

    def any_modification_exists(self) -> bool:
        if self.modified_files_exists() or self.deleted_files_exists() or self.untracked_files_exists():
            return True
        return False

    def modified_files_exists(self) -> bool:
        if len(self.diff_object.files_modified) > 0:
            return True
        return False

    def deleted_files_exists(self) -> bool:
        if len(self.diff_object.files_deleted) > 0:
            return True
        return False

    def untracked_files_exists(self) -> bool:
        if len(self.diff_object.files_untracked) > 0:
            return True
        return False

    def get_files_modified(self) -> str:
        if not self.modified_files_exists():
            return ''
        files_modified = 'Files modified:\n'
        for filename in self.diff_object.files_modified:
            files_modified += f'\t{filename}\n'
        return files_modified

    def get_files_deleted(self) -> str:
        if not self.deleted_files_exists():
            return ''
        files_deleted = 'Files deleted:\n'
        for filename in self.diff_object.files_deleted:
            files_deleted += f'\t{filename}\n'
        return files_deleted

    def get_files_untracked(self) -> str:
        if not self.untracked_files_exists():
            return ''
        file_untracked = 'Files untracked:\n'
        for filename in self.diff_object.files_untracked:
            file_untracked += f'\t{filename}\n'
        return file_untracked
