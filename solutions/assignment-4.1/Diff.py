import vcs_files
import Object
import os
from typing import Union, Dict, Set, List


class diff():
    """docstring for Diff"""

    def __init__(self, commit_object):
        self.insertions: int = 0
        self.deletions: int = 0
        self.modification_log: str = ''
        self.files_untracked: Set[str] = set()
        self.files_deleted: Dict[str, Union[Object.tree, Object.blob]] = dict()
        self.files_modified: Dict[str, Union[Object.tree, Object.blob]] = dict()
        self._compare_dir_and_object('.', commit_object.get_tree())

    # A recursive function which will compare the complete directory structure
    def _compare_dir_and_object(self, dir_path, tree_object):
        for filename in os.listdir(dir_path):
            filepath = os.path.join(dir_path, filename)
            if os.path.isdir(filepath):
                if filename == vcs_files.ROOT:
                    continue
                if filename not in tree_object.trees:
                    self.files_untracked.add(filepath)
                    continue
                self._compare_dir_and_object(filepath, tree_object.trees[filename])
                continue
            if filename not in tree_object.blobs:
                self.files_untracked.add(filepath)
                continue
            difference_calculator = Diff_file(filepath, os.path.join(vcs_files.OBJECTS, tree_object.blobs[filename].get_hash()))
            if difference_calculator.insertions + difference_calculator.deletions > 0:
                self.insertions += difference_calculator.insertions
                self.deletions += difference_calculator.deletions
                self.modification_log += f'\nChanges in file "{filepath}" : {difference_calculator.modification_log}'
                self.files_modified[filepath] = tree_object.blobs[filename]

        for filename in tree_object.blobs:
            if filename not in os.listdir(dir_path):
                self.files_deleted[os.path.join(dir_path, filename)] = tree_object.blobs[filename]
        for filename in tree_object.trees:
            if filename not in os.listdir(dir_path):
                self.files_deleted[os.path.join(dir_path, filename)] = tree_object.trees[filename]


class Diff_file(object):
    def __init__(self, new_file, old_file):
        self.new_file_lines: List[str] = []
        self.old_file_lines: List[str] = []
        self.common_line_list: List[str] = []
        self.insertions: int = 0
        self.deletions: int = 0
        self.modification_log: str = ''
        self._set_file_lines(new_file, old_file)
        self.common_line_list: List[str] = self._lcs()
        self._difference_details()

    def _set_file_lines(self, new_file, old_file):
        with open(new_file, 'r') as read_new_file:
            self.new_file_lines = read_new_file.read().split('\n')
        with open(old_file, 'r') as read_old_file:
            self.old_file_lines = read_old_file.read().split('\n')

    def _lcs(self):
        compare_matrix = [[0 for _ in range(len(self.old_file_lines) + 1)] for _ in range(len(self.new_file_lines) + 1)]
        common_line = []
        for index1, element1 in enumerate(self.new_file_lines, start=1):
            for index2, element2 in enumerate(self.old_file_lines, start=1):
                if element1 is None or element2 is None:
                    continue
                if element1 == element2:
                    compare_matrix[index1][index2] = compare_matrix[index1 - 1][index2 - 1] + 1
                else:
                    compare_matrix[index1][index2] = max(compare_matrix[index1 - 1][index2 - 1], max(compare_matrix[index1 - 1][index2], compare_matrix[index1][index2 - 1]))

        row = len(self.new_file_lines)
        col = len(self.old_file_lines)
        while row != 0 and col != 0:
            # print(row,col)
            if col > 0 and compare_matrix[row][col] == compare_matrix[row][col - 1]:
                col = col - 1
            elif row > 0 and compare_matrix[row][col] == compare_matrix[row - 1][col]:
                row = row - 1
            else:
                common_line.append((row - 1, col - 1))
                col = col - 1
                row = row - 1
        common_line.reverse()
        return common_line

    def _difference_details(self):
        self.insertions: int = 0
        self.deletions: int = 0
        self.modification_log: str = ''
        new_file_pointer = 0
        old_file_pointer = 0

        for line_in_new_file, line_in_old_file in self.common_line_list:
            while old_file_pointer < line_in_old_file:
                self.modification_log += f"-- {self.old_file_lines[old_file_pointer]}\n"
                old_file_pointer = old_file_pointer + 1
                self.deletions = self.deletions + 1
            old_file_pointer = line_in_old_file + 1
            while new_file_pointer < line_in_new_file:
                self.modification_log += f"++ {self.new_file_lines[new_file_pointer]}\n"
                new_file_pointer = new_file_pointer + 1
                self.insertions = self.insertions + 1
            new_file_pointer = line_in_new_file + 1
            self.modification_log += f"{self.new_file_lines[line_in_new_file]}\n"

        while old_file_pointer < len(self.old_file_lines):
            self.modification_log += f"-- {self.old_file_lines[old_file_pointer]}\n"
            old_file_pointer = old_file_pointer + 1
            self.deletions = self.deletions + 1
        while new_file_pointer < len(self.new_file_lines):
            self.modification_log += f"++ {self.new_file_lines[new_file_pointer]}\n"
            new_file_pointer = new_file_pointer + 1
            self.insertions = self.insertions + 1
        self.modification_log = f"++{self.insertions} --{self.deletions}\n---------------------------\n{self.modification_log}\n"
