import os
import time
import objects
import logging
import json

class Ngc:

    USER_NAME = 'user_name'
    USER_EMAIL = 'user_email'
    TIMESTAMP = 'timestamp'

    def __init__(self, repo_path=os.getcwd()):
        self.repo_path = repo_path
        self.user_details = self._get_user_details()
        self.author_details = {self.USER_NAME : None,
                               self.USER_EMAIL : None,
                               self.TIMESTAMP : None}
        self.head = None
        self.obj_blob = objects.Blob()
        self.obj_tree = objects.Tree(self.create_logger("Tree log"), self.repo_path)
        self.obj_commit = objects.Commit(self.repo_path)

    def init(self):
        self.author_details = self.user_details
        ngc_path = os.path.join(self.repo_path, ".ngc")
        objects_path = os.path.join(ngc_path, "objects")

        if not os.path.exists(ngc_path): os.makedirs(ngc_path)
        if not os.path.exists(objects_path): os.makedirs(objects_path)

    def status(self):
        #TODO:
        #   check for files removed
        #   check for files added
        print(f"On branch {self.head}")
        print("Changes not committed:")
        self._check_modified_files()
        print('Use "ngc commit" to add changes to a new commit')

    def diff(self):
        pass

    def commit(self, message):
        tree_hash = self.obj_tree.create()
        parent_hash = self._get_current_commit_hash()
        self.user_details[self.TIMESTAMP] = time.time()
        commit_hash = self.obj_commit.create(tree_hash=tree_hash, author_details=self.author_details, committer_details=self.user_details, message=message, parent_hash=parent_hash)
        self._update_commit_hash(commit_hash)

    def reset(self):
        pass

    def log(self, commit_hash=None):
        if commit_hash is None: commit_hash = self.head

        with open(os.path.join(self.repo_path, '.ngc/HEAD'), 'rb') as head_file:
            current_hash = head_file.read().decode()

        while True:
            if current_hash == commit_hash:
                break
            else:
                with open(os.path.join(self.repo_path, f'.ngc/objects/{current_hash}'), 'rb') as commit_file:
                    commit_data = json.load(commit_file)
                current_hash = commit_data[self.obj_commit.PARENT]

        while True:
            self.obj_commit.print_commit_data(current_hash)
            with open(os.path.join(self.repo_path, f'.ngc/objects/{current_hash}'), 'rb') as commit_file:
                commit_data = json.load(commit_file)
            if self.obj_commit.PARENT not in commit_data: break
            else: current_hash = commit_data[self.obj_commit.PARENT]


    def checkout(self):
        pass

    def config_user(self, user_name, user_email):
        self.user_details[self.USER_NAME] = user_name
        self.user_details[self.USER_EMAIL] = user_email

        with open(os.path.join(self.repo_path, ".userinfo"), 'w') as user_info_file:
            json.dump(self.user_details, user_info_file)

    def _get_user_details(self):
        info_file_path = os.path.join(self.repo_path, ".userinfo")
        user_details = {self.USER_NAME : None,
                        self.USER_EMAIL : None,
                        self.TIMESTAMP : None}

        if os.path.exists(info_file_path):
            with open(info_file_path, "r") as user_info_file:
                user_details = json.load(user_info_file)

        return user_details

    def _get_current_commit_hash(self):
        commit_hash = None
        try:
            with open(os.path.join(self.repo_path, ".ngc/HEAD"), "r") as head_file:
                commit_hash = head_file.read()
        except FileNotFoundError:
            pass
        return commit_hash

    def _update_commit_hash(self, new_commit_hash):
        self.head = new_commit_hash

        with open(os.path.join(self.repo_path, ".ngc/HEAD"), "w") as head_file:
            head_file.write(new_commit_hash)

    def _check_modified_files(self, tree=None, path=None):
        if path is None : path = self.repo_path
        if tree is None : tree = self.head

        if tree is self.head:
            with open(os.path.join(self.repo_path, ".ngc/objects", tree), "rb") as commit_file:
                commit_data = json.load(commit_file)
            tree = commit_data[self.obj_commit.TREE]
        with open(os.path.join(self.repo_path, ".ngc/objects", tree), "rb") as tree_file:
            tree_json = json.load(tree_file)
        for file in tree_json[self.obj_tree.FILES]:
            file_modified_time = os.stat(os.path.join(path, file)).st_mtime
            blob_modified_time = os.stat(os.path.join(self.repo_path, ".ngc/objects", tree_json[self.obj_tree.FILES][file])).st_mtime
            if file_modified_time > blob_modified_time:
                print(f"modified:    {file}")
        for subdir in tree_json[self.obj_tree.SUBDIRS]:
            new_path = os.path.join(path, subdir)
            new_tree = tree_json[self.obj_tree.SUBDIRS][subdir]
            self._check_modified_files(tree=new_tree, path=new_path)

    @staticmethod
    def create_logger(logger_name, log_level=logging.WARNING):

        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

        return logger
