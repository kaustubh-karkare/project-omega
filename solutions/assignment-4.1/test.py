import os
import shutil
import vcs_files
import Object
import Init
import Commit
import Diff
import Status
import Reset
import Checkout
import unittest


class TestVCS(unittest.TestCase):

    def make_changes(self, file_structure):
        for filename in file_structure:
            try:
                os.makedirs(os.path.dirname(os.path.realpath(filename)))
            except FileExistsError:
                pass
            finally:
                with open(filename, 'w') as write_file:
                    write_file.write(file_structure[filename])

    def clean_directory(self):
        for filename in os.listdir():
            if os.path.isdir(filename):
                shutil.rmtree(filename)
                continue
            os.remove(filename)

    def setUp(self):
        test_dir = 'test_dir'
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)
        os.chdir(test_dir)

    def test_init(self):
        result = Init.init()
        self.assertEqual(result.status, 'Initializing vcs in this directory')
        self.assertTrue(os.path.exists(vcs_files.ROOT))
        result = Init.init()
        self.assertEqual(result.status, 'Reinitializing vcs in this directory')

    def test_commit(self):
        Init.init()

        file_structure = {
            'test.txt': 'initial blob'
        }
        self.make_changes(file_structure)
        commit_handler = Commit.commit(message='first_commit')
        self.assertEqual(commit_handler.status, None)
        first_commit = Object.get_HEAD()
        self.assertEqual(first_commit.get_message(), 'first_commit')
        tree_obj = first_commit.get_tree()
        self.assertTrue('test.txt' in tree_obj.blobs)
        blob_obj = tree_obj.blobs['test.txt']
        self.assertTrue(blob_obj.get_content(), file_structure['test.txt'])

        file_structure = {
            'test.txt': 'final blob'
        }
        self.make_changes(file_structure)
        Commit.commit(message='second_commit')
        second_commit = Object.get_HEAD()
        self.assertEqual(second_commit.get_parent().get_hash(), first_commit.get_hash())

        file_structure = {
            'dir/test.txt': 'testing tree entries'
        }
        self.make_changes(file_structure)
        Commit.commit(message='third_commit')
        third_commit = Object.get_HEAD()
        tree_obj = third_commit.get_tree()
        self.assertTrue('dir' in tree_obj.trees)
        tree_obj = tree_obj.trees['dir']
        self.assertTrue('test.txt' in tree_obj.blobs)
        blob_obj = tree_obj.blobs['test.txt']
        self.assertTrue(blob_obj.get_content(), file_structure['dir/test.txt'])

        commit_handler = Commit.commit(message='fourth_commit')
        self.assertEqual(commit_handler.status, 'Clean working directory\nNothing to commit')

    def test_diff(self):
        Init.init()
        Commit.commit()

        file_structure = {
            'test.txt': '''
                initial blob
                testing changes'''
        }
        self.make_changes(file_structure)
        difference = Diff.diff(Object.get_HEAD())
        self.assertTrue('.\\test.txt' in difference.files_untracked)

        Commit.commit()
        file_structure = {
            'test.txt': '''
                final blob
                testing changes'''
        }
        self.make_changes(file_structure)
        difference = Diff.diff(Object.get_HEAD())
        self.assertTrue('.\\test.txt' in difference.files_modified)
        expected_modification_log = r'''
Changes in file ".\test.txt" : ++1 --1
---------------------------

--                 initial blob
++                 final blob
                testing changes

'''
        self.assertEqual(difference.modification_log, expected_modification_log)

        os.remove('test.txt')
        difference = Diff.diff(Object.get_HEAD())
        self.assertTrue('.\\test.txt' in difference.files_deleted)

    def test_status(self):
        Init.init()
        Commit.commit()
        file_structure = {
            'animals/dog': 'dog',
            'animals/cat': 'cat',
        }
        self.make_changes(file_structure)
        status = Status.status()
        self.assertEqual(status.get_files_modified(), '')
        self.assertEqual(status.get_files_deleted(), '')
        self.assertEqual(status.get_files_untracked(), 'Files untracked:\n\t.\\animals\n')

        Commit.commit()
        file_structure = {
            'animals/dog': 'Husky',  # Modification
            'birds/parrot': 'parrot'  # New file
        }
        self.make_changes(file_structure)
        os.remove('animals/cat')  # File deletion
        status = Status.status()
        self.assertEqual(status.get_files_modified(), 'Files modified:\n\t.\\animals\\dog\n')
        self.assertEqual(status.get_files_deleted(), 'Files deleted:\n\t.\\animals\\cat\n')
        self.assertEqual(status.get_files_untracked(), 'Files untracked:\n\t.\\birds\n')

        Commit.commit()
        status = Status.status()
        self.assertFalse(status.any_modification_exists())

    def test_reset(self):
        Init.init()
        Commit.commit()

        file_structure = {
            'animals/dog': 'dog',
            'animals/cat': 'cat',
            'birds/parrot': 'parrot'
        }
        self.make_changes(file_structure)
        Commit.commit()

        file_structure = {
            'animals/dog': 'Huskey',  # Modification
            'birds/peacock': 'peacock'  # New File
        }
        self.make_changes(file_structure)
        with open('animals/dog', 'r') as read_file:
            self.assertEqual(read_file.read(), 'Huskey')
        Reset.reset(commit=Object.get_HEAD(), soft=True, hard=False)  # Soft Reset
        with open('animals/dog', 'r') as read_file:
            self.assertEqual(read_file.read(), 'dog')
        self.assertTrue(os.path.exists('birds/peacock'))

        file_structure = {
            'animals/dog': 'Huskey',  # Modification
            'birds/peacock': 'peacock'  # New File
        }
        self.make_changes(file_structure)
        Reset.reset(commit=Object.get_HEAD(), soft=False, hard=True)  # Hard Reset
        with open('animals/dog', 'r') as read_file:
            self.assertEqual(read_file.read(), 'dog')
        self.assertFalse(os.path.exists('birds/peacock'))

        file_structure = {
            'animals/dog': 'Huskey',  # Modification
            'birds/peacock': 'peacock'  # New File
        }
        self.make_changes(file_structure)
        Reset.reset(commit=Object.get_HEAD().get_parent(), soft=False, hard=True)  # Hard Reset on First commit when the working directory was empty
        self.assertFalse(os.path.exists('animals'))
        self.assertFalse(os.path.exists('birds'))

    def test_checkout(self):
        Init.init()
        Commit.commit()
        first_commit = Object.get_HEAD()

        file_structure = {
            'animals/dog': 'dog',
            'animals/cat': 'cat',
            'birds/parrot': 'parrot'
        }
        self.make_changes(file_structure)
        Commit.commit()
        second_commit = Object.get_HEAD()

        checkout = Checkout.checkout(old_commit=second_commit, new_commit=first_commit)
        result = checkout.make_changes()
        self.assertFalse(os.path.exists('animals'))
        self.assertFalse(os.path.exists('birds'))
        self.assertEqual(Object.get_HEAD().get_hash(), first_commit.get_hash())
        self.assertEqual(result, f'Updated head : {Object.get_HEAD().get_hash()}')

        checkout = Checkout.checkout(old_commit=first_commit, new_commit=second_commit)
        result = checkout.make_changes()
        self.assertEqual(result, f'Updated head : {second_commit.get_hash()}')

        file_structure = {
            'animals/dog': 'Huskey'
        }
        self.make_changes(file_structure)
        Commit.commit()
        third_commit = Object.get_HEAD()

        checkout = Checkout.checkout(old_commit=third_commit, new_commit=second_commit)
        result = checkout.make_changes()
        with open('animals/dog', 'r') as read_file:
            self.assertEqual(read_file.read(), 'dog')  # Content of second commit
        self.assertEqual(result, f'Updated head : {second_commit.get_hash()}')
        self.assertEqual(Object.get_HEAD().get_hash(), second_commit.get_hash())

        file_structure = {
            'animals/dog': 'Shepherd'   # File Modified
        }
        self.make_changes(file_structure)
        checkout = Checkout.checkout(old_commit=second_commit, new_commit=third_commit)
        result = checkout.make_changes()
        self.assertEqual(result, 'Aborting checkout\nUnsaved changes detected\n.\\animals\\dog is modified and needs to be committed before checkout')

        os.remove('animals/dog')        # File Deleted
        checkout = Checkout.checkout(old_commit=second_commit, new_commit=third_commit)
        result = checkout.make_changes()
        self.assertEqual(result, 'Aborting checkout\nUnsaved changes detected\n.\\animals\\dog is modified and needs to be committed before checkout')

    def tearDown(self):
        os.chdir('../')
        shutil.rmtree('test_dir')


if __name__ == '__main__':
    unittest.main()
