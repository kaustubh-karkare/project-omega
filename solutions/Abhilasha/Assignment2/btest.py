import unittest
import os
from os import path
import tempfile
import shutil
import BuildAutomationTool as BAT


class TestBuildAutomationTool(unittest.TestCase):

    def setUp(self):

        self.root = os.getcwd()
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):

        shutil.rmtree(self.test_dir)

    def test_build_test_all_and_test_clean(self):

        with self.test_dir as tmpdirname:
            new_root_dir = tmpdirname+os.path.sep+"code"
            shutil.copytree(self.root+os.path.sep+"code", new_root_dir)
            os.chdir(new_root_dir)
            executor = BAT.ActionExecutor(new_root_dir)
            executor.execute('build', 'test_all')
            self.assertEqual(path.exists('test.o'), True)
            self.assertEqual(path.exists('test_sort_bubble.exe'), True)
            self.assertEqual(path.exists('test_sort_quick.exe'), True)
            self.assertEqual(path.exists('test_sort_merge.exe'), True)
            os.chdir(os.path.join("algorithms"))
            self.assertEqual(path.exists('sort_bubble.o'), True)
            self.assertEqual(path.exists('sort_quick.o'), True)
            self.assertEqual(path.exists('sort_merge.o'), True)

            os.chdir(new_root_dir)
            executor.execute('build', 'clean')
            self.assertEqual(path.exists('test.o'), False)
            self.assertEqual(path.exists('test_sort_bubble.exe'), False)
            self.assertEqual(path.exists('test_sort_quick.exe'), False)
            self.assertEqual(path.exists('test_sort_merge.exe'), False)
            os.chdir(os.path.join("algorithms"))
            self.assertEqual(path.exists('sort_bubble.o'), False)
            self.assertEqual(path.exists('sort_quick.o'), False)
            self.assertEqual(path.exists('sort_merge.o'), False)
            os.chdir(self.root)

    def test_sort_merge(self):

        with self.test_dir as tmpdirname:
            new_root_dir = tmpdirname+os.path.sep+"code"
            shutil.copytree(self.root+os.path.sep+"code", new_root_dir)
            os.chdir(new_root_dir)
            executor = BAT.ActionExecutor(new_root_dir)
            executor.execute('build', 'test_sort_merge')
            self.assertEqual(path.exists('test.o'), True)
            self.assertEqual(path.exists('test_sort_merge.exe'), True)
            self.assertEqual(path.exists('test_sort_bubble.exe'), False)
            self.assertEqual(path.exists('test_sort_quick.exe'), False)
            os.chdir(os.path.join("algorithms"))
            self.assertEqual(path.exists('sort_merge.o'), True)
            self.assertEqual(path.exists('sort_bubble.o'), False)
            self.assertEqual(path.exists('sort_quick.o'), False)
            os.chdir(self.root)

    def test_invalid_key(self):

        with self.test_dir as tmpdirname:
            new_root_dir = tmpdirname+os.path.sep+"code"
            shutil.copytree(self.root+os.path.sep+"code", new_root_dir)
            os.chdir(new_root_dir)
            executor = BAT.ActionExecutor(new_root_dir)
            with self.assertRaisesRegex(Exception, 'Command not recognized.'):
                executor.execute('build', 'test_sort_selection')
            os.chdir(self.root)


if __name__ == '__main__':

    unittest.main()
