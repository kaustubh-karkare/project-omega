require 'fileutils'
require_relative 'blob'
require_relative 'vcs_internals'


SHA_SIZE = 40


def build_tree(directory_path)
    files = {}
    for element in Dir.glob(File.join(directory_path, '*'))
        file_name = File.basename(element)
        if File.file?(element)
            sha_hash = create_blob(element)
            files[file_name] = sha_hash
        else
            sha_hash = build_tree(element)
            files[file_name] = sha_hash
        end
    end
    content = ""
    files.each do |file_name, sha_hash|
        content = content + file_name + NULL + sha_hash
    end
    header = "tree #{content.length}#{NULL}"
    sha_hash = get_sha_hash(header, content)
    hash_object(header, content, sha_hash)
    return sha_hash
end


def get_directory_content(sha_hash)
    input_file_path = File.join(Dir.getwd, ".vcs", "objects", sha_hash)
    header = nil
    files = {}
    open(input_file_path, "r") do |input_file|
        data = ""
        while not data.include? NULL
            current_data = input_file.read(BLOCK_SIZE)
            if current_data.nil?
                break
            end
            data += current_data
        end

        header, _separator, data = data.partition(NULL)
        while true
            while not data.include? NULL
                current_data = input_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += current_data
            end
            if data.empty?
                break
            end
            file_name, _separator, data = data.partition(NULL)
            while data.length < SHA_SIZE
                current_data = input_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += input
            end
            file_sha_hash = data[0,SHA_SIZE]
            data = data[SHA_SIZE..-1]
            files[file_name] = file_sha_hash
        end
    end
    return files
end


def delete_working_directory(directory_path=Dir.getwd)
    for element in Dir.glob(File.join(directory_path, '*'))
        FileUtils.remove_entry(element)
    end
end


def build_working_directory(sha_hash, directory_path)
    files = get_directory_content(sha_hash)
    files.each do |file_name, sha_hash|
        if type(sha_hash).to_s.eql?("blob")
            restore_blob(sha_hash, File.join(directory_path, file_name))
        else
            Dir.mkdir(File.join(directory_path, file_name))
            build_working_directory(
                sha_hash,
                File.join(directory_path, file_name)
            )
        end
    end
end


def get_modified_files(directory_path=Dir.getwd)
    modified_files = {}
    for element in Dir.glob(File.join(directory_path, '*'))
        if File.file?(element)
            header = "blob #{File.size(element)}#{NULL}"
            sha_hash = get_sha_hash(header, element)
            if not File.file? \
                    (File.join(Dir.getwd, ".vcs", "objects", sha_hash))
                modified_files[element] = sha_hash
            end
        else
            modified_files.merge(get_modified_files(element))
        end
    end
    return modified_files
end
