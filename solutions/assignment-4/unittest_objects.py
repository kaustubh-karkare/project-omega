import unittest
import tempfile
import random
import string
import os
from distutils.dir_util import copy_tree
import logging
import objects

class ObjectsTest(unittest.TestCase):
    TEST_DIR = os.path.join(os.getcwd(),'test/test_dir')

    FILE_LIST = {'file1':'b75caba50711332063088fc53744f1c55b4445fe',
                 'subdir1/file2':'bfc385898eb83d5f15e84635a1ab1649cced4fcb',
                 'subdir2/file3':'41cd77870f7d97e5b5a32b87a12343312ffbc065',
                 'subdir2/subdir3/file4':'f0ef9dfd4b499f54cdcc15d0fc95204d92207790'}

    SUBDIR_LIST = {'.':'0fbd657ff0d946213275023ae722c244c3026682',
                   'subdir1':'d2b945ace691fe8522e868ebde016d0a53ac40ca',
                   'subdir2':'35d9d594f1d830505fb3132d8959e73119755114',
                   'subdir2/subdir3':'17aeddcc4d19a24eedc6024163cdb9b0fceb5faa'}

    def test_blob(self):
        blob_obj = objects.Blob()

        for file in self.FILE_LIST:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(self.TEST_DIR, file)
                file_name = blob_obj.create(file_path, temp_dir)
                blob_path = os.path.join(temp_dir,file_name)
                self.assertEqual(file_name, self.FILE_LIST[file])

                blob_file_header = blob_obj.read_header(blob_path)
                file_header = f"blob {os.stat(file_path).st_size}\x00"
                self.assertEqual(blob_file_header, file_header)

                with open(file_path, 'rb') as f:
                    file_data = f.read().decode()
                blob_file_data = blob_obj.get_content(blob_path)
                self.assertEqual(file_data, blob_file_data)


    def test_tree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copy_tree(self.TEST_DIR, temp_dir)
            tree_obj = objects.Tree(self.create_logger('tree_logger'), path=temp_dir)
            tree_obj.create()
            for subdir in self.SUBDIR_LIST:
                tree_path = os.path.join(tree_obj.obj_path, self.SUBDIR_LIST[subdir])
                self.assertTrue(os.path.exists(tree_path))

    def test_commit(self):
        commit_data = {"tree": "0fbd657ff0d946213275023ae722c244c3026682",
                       "author": None,
                       "committer": None,
                       "message": "test"}

        with tempfile.TemporaryDirectory() as temp_dir:
            copy_tree(self.TEST_DIR, temp_dir)
            tree_obj = objects.Tree(self.create_logger('tree_logger'), path=temp_dir)
            commit_obj = objects.Commit(path=temp_dir)
            tree_obj.create()
            commit_hash = commit_obj.create(tree_hash=self.SUBDIR_LIST["."],
                                            author_details=None,
                                            committer_details=None,
                                            message="test")
            commit_path = os.path.join(commit_obj.obj_path, commit_hash)
            self.assertTrue(os.path.exists(commit_path))

            commit_json_data = commit_obj.get_commit_dict(commit_hash)
            self.assertEqual(commit_data, commit_json_data)

    @staticmethod
    def create_logger(logger_name, log_level=logging.WARNING):
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

        return logger


if __name__ == '__main__':
    unittest.main()
