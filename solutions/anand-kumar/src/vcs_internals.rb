require 'digest/sha1'
require_relative 'file_storage'


BLOCK_SIZE = 1024
NULL = "\0"

    
class FilePath
    VCS = File.join(Dir.getwd, ".vcs")
    HEAD = File.join(VCS, "HEAD")
    OBJECTS = File.join(VCS, "objects")
    CONFIG = File.join(VCS, "config")
end


def extract_header(input_file)
    data = ""
    while not data.include? NULL
        current_data = input_file.read(BLOCK_SIZE)
        if current_data.nil?
            break
        end
        data += current_data
    end
    header, _separator, content = data.partition(NULL)
    return header, content
end


def type(sha_hash)
    input_file_path = File.join(FilePath::OBJECTS, sha_hash)
    header = ""
    _content = ""
    open(input_file_path, "r") do |input_file|
        header, _separator, _content = extract_header(input_file)
    end
    return %r{[a-z]+}.match(header).to_s
end


def get_sha_hash(header, path_or_content)
    sha1 = Digest::SHA1.new
    sha1.update(header)
    if not path_or_content.include? NULL and File.file? path_or_content
        open(content_file_path=path_or_content, "r") do |content_file|
            while true
                data = content_file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                sha1.update(data)
            end
        end
    else
        sha1.update(content=path_or_content)
    end
    return sha1.hexdigest.to_s
end


def create_object_file(header, path_or_content, sha_hash)
    output_file_path = File.join(FilePath::OBJECTS, sha_hash)
    open(output_file_path, "w") do |output_file|
        output_file.write(header)
        if not path_or_content.include? NULL and File.file? path_or_content
            open(content_file_path=path_or_content, "r") do |content_file|
                while true
                    data = content_file.read(BLOCK_SIZE)
                    if data.nil?
                        break
                    end
                    output_file.write(data)
                end
            end
        else
            output_file.write(content=path_or_content)
        end
    end
end


def get_files_in_directory(directory_path=Dir.getwd)
    files = {}
    for element in Dir.glob(File.join(directory_path, '*'))
        if File.file? element
            header = "blob #{File.size(element)}#{NULL}"
            sha_hash = get_sha_hash(header, element)
            files[element] = sha_hash
        else
            files = files.merge(get_files_in_directory(element))
        end
    end
    return files
end


def get_files_in_tree(sha_hash, directory_path=Dir.getwd)
    files_in_commit = {}
    files_in_current_node = {}
    files_in_current_node = Tree.get_directory_content(sha_hash)
    files_in_current_node.each do |file_name, sha_hash|
        if type(sha_hash).eql? "blob"
            files_in_commit[File.join(directory_path, file_name)] = sha_hash
        else
            files_in_commit = files_in_commit.merge(
                get_files_in_tree(
                    sha_hash,
                    File.join(directory_path, file_name)
                )
            )
        end
    end
    return files_in_commit
end


def get_modified_files(**kwargs)
    old_files = {}
    new_files = {}
    old_commit = kwargs.fetch(:old_commit, File.read(FilePath::HEAD))
    new_commit = kwargs.fetch(:new_commit, nil)
    directory_path = kwargs.fetch(:directory_path, Dir.getwd)
    if not old_commit.empty?
        old_commit_object_content = Commit.parse_commit_object(old_commit)
        old_files = get_files_in_tree(old_commit_object_content["sha"])
    end
    if new_commit != nil
        new_commit_object_content = Commit.parse_commit_object(new_commit)
        new_files = get_files_in_tree(new_commit_object_content["sha"])
    else
        new_files = get_files_in_directory(directory_path)
    end
    modified_files = []
    new_files.each do |file_name, new_sha|
        if old_files.key? file_name
            if new_sha != old_files[file_name]
                modified_files.push(
                    {
                        :file_name => file_name,
                        :old_sha => old_files[file_name],
                        :new_sha => new_sha,
                    }
                )
            end
        else
            modified_files.push(
                {
                    :file_name => file_name,
                    :new_sha => new_sha,
                }
            )
        end
    end
    old_files.each do |file_name, old_sha|
        if not new_files.key? file_name
            modified_files.push(
                {
                    :file_name => file_name,
                    :old_sha => old_sha,
                }
            )
        end
    end
    return modified_files
end
