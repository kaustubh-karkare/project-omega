/* 
 *  Ankur Dubey
 *  Requires -lboost_system and -lboost_filesystem flags to compile.
 */

#include<iostream>
#include<string>
#include<vector>
#include<queue>
#include<set>
#include<boost/filesystem.hpp>

#define SHOW_FILES_SCANNED false

class NoFilesInDirectoryException : public std::exception {
	public: const char* what () const throw () {
    	return "No files were found in directory";
    }
};

/* 
 * Returns maximum size and list of files having maximum size
 */
std::pair<uintmax_t, std::vector<std::string>> max_files(const std::string &path_string, bool show_files_scanned) {
   
    using namespace boost::filesystem;
    
    path root(path_string);
    directory_iterator end_itr;
    std::queue<path> directory_queue; 
    std::set<path> visited;
    directory_queue.push(root);
    
    uintmax_t max_file_size = 0;   // Max file size
    std::set<path> max_file_paths; // Will contain paths for all files having maximum size
    bool directory_contains_file = false;

    /* 
     * We run a breadth first search on filesystem tree rooted at given path. 
     * If a directory is encountered push it in the queue, else
     * if a file is encountered check it's size.
     */
    while(!directory_queue.empty()) {
        auto front = directory_queue.front();
        directory_queue.pop();
        for(directory_iterator itr(front); itr != end_itr; ++itr) {
            if(is_regular_file(itr->path())) {
                auto size = file_size(itr->path());
                if(max_file_size < size) {
                    max_file_paths.clear();
                    max_file_paths.insert(itr->path());
                    max_file_size = size;
                } else if (max_file_size == size) {
                    max_file_paths.insert(itr->path());
                }
                if(show_files_scanned) {
                    std::cout << itr->path() << " " << size << " bytes\n";
                }
                directory_contains_file = true;
            } else if(is_directory(itr->path())) {
                directory_queue.push(itr->path());
            }
        }
    }

    //Throw an error if no files were found in tree.
    if(!directory_contains_file) {
        throw NoFilesInDirectoryException();
    }

    std::vector<std::string> path_strings;
    for(auto &path: max_file_paths) {
        path_strings.push_back(path.string());
    }

    return make_pair(max_file_size, path_strings);
}

int main(int argc, char *argv[]) {
    if(argc == 1) {
        std::cout << "Usage: explore <path>\n";
        std::cout << "Supports both relative and absolute paths\n";
        return 0;
    }
    try {
        auto result = max_files(argv[1], SHOW_FILES_SCANNED);
        std::cout << "Maximum file size of " << result.first << " bytes reported for following files:\n";
        for(auto &str: result.second) {
            std::cout << str << "\n";
        }
    } catch (const boost::filesystem::filesystem_error& ex) {
        std::cout << ex.what();
    } catch (const NoFilesInDirectoryException& ex) {
        std::cout << ex.what();
    }
    return 0;
}