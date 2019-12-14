import os
import vcs_files


class init(object):
    FILE_STRUCTURE = {
        vcs_files.ROOT: 'dir',
        vcs_files.OBJECTS: 'dir',
        vcs_files.REFS: 'dir',
        vcs_files.MASTER: 'file',
        vcs_files.HEAD: 'file'
    }

    def __init__(self):
        self.status = None
        if os.path.exists(vcs_files.ROOT):
            self.status = 'Reinitializing vcs in this directory'
        else:
            self.status = 'Initializing vcs in this directory'
        self.check_and_create_files()

    def check_and_create_files(self):
        for filename in self.FILE_STRUCTURE:
            if self.FILE_STRUCTURE[filename] == 'dir':
                try:
                    os.makedirs(os.path.realpath(filename))
                except FileExistsError:
                    pass
                continue
            try:
                os.makedirs(os.path.dirname(os.path.realpath(filename)))
            except FileExistsError:
                pass
            finally:
                with open(filename, 'w') as newfile:
                    newfile.write('')
