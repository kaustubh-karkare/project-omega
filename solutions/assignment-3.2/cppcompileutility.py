import os
import json


class CompileCppFiles:

    def __init__(self, directory):
        self.file_list_path = os.path.join(directory, 'file_list')
        files_to_compile = self.get_cpp_files_to_compile(directory)
        self.update_file_list(directory)
        self.compile_files(files_to_compile)

    def get_cpp_files_to_compile(self, directory):
        valid_extensions = \
            ['.C', '.cc', '.cpp', '.CPP', '.c++', '.cp', '.cxx']
        files_to_compile = []
        if not os.path.isfile(self.file_list_path):
            file_list = open(self.file_list_path, 'w+')
        else:
            file_list = open(self.file_list_path, 'r+')
        for file in os.listdir(directory):
            extension = None
            if file.rfind('.') != -1:
                extension = file[file.rfind('.'):]
            else:
                continue
            is_acceptable_extension = False
            for available_extension in valid_extensions:
                if extension == available_extension:
                    is_acceptable_extension = True
                    break
            if not is_acceptable_extension:
                continue
            file_list.seek(0)
            try:
                decoded_file_list = json.load(file_list)
            except ValueError:
                decoded_file_list = {}
            file_found = False
            for key, value in decoded_file_list.items():
                last_modified = None
                if key == file:
                    file_found = True
                    last_modified = \
                        os.path.getmtime(os.path.join(directory, file))
                else:
                    continue
                if value == last_modified:
                    break
                else:
                    decoded_file_list[key] = last_modified
                    files_to_compile \
                        .append(os.path.join(directory, "'" + file + "'"))
                    break
            if not file_found:
                decoded_file_list[file] = \
                    os.path.getmtime(os.path.join(directory, file))
                files_to_compile \
                    .append(os.path.join(directory, "'" + file + "'"))
            file_list.seek(0)
            file_list.truncate()
            json.dump(decoded_file_list, file_list)
        file_list.close()
        return files_to_compile

    def update_file_list(self, directory):
        with open(self.file_list_path, 'r+') as file_list:
            decoded_file_list = json.load(file_list)
            for key, value in decoded_file_list.items():
                file_exists_in_directory = False
                for element in os.listdir(directory):
                    if element == key:
                        file_exists_in_directory = True
                        break
                if not file_exists_in_directory:
                    del decoded_file_list[key]
            file_list.seek(0)
            file_list.truncate()
            json.dump(decoded_file_list, file_list)

    def compile_files(self, files_to_compile):
        for file in files_to_compile:
            os.system('g++ ' + file)
