require 'fileutils'
require_relative 'vcs_internals'


SHA_SIZE = 40


class Blob

    def self.create_blob(content_file_path)
        header = "blob #{File.size(content_file_path)}#{NULL}"
        sha_hash = get_sha_hash(header, content_file_path)
        create_object_file(header, content_file_path, sha_hash)
        return sha_hash
    end

    def self.restore_blob(sha_hash, output_file_path)
        input_file_path = File.join(FilePath::OBJECTS, sha_hash)
        open(input_file_path, "r") do |input_file|
            open(output_file_path, "w") do |output_file|
                data = ""
                _header, data = extract_header(input_file)
                output_file.write(data)
                while true
                    data = input_file.read(BLOCK_SIZE)
                    if data.nil?
                        break
                    end
                    output_file.write(data)
                end
            end
        end
    end
end


class Tree

    def self.build_tree(directory_path)
        files = {}
        for element in Dir.glob(File.join(directory_path, '*'))
            file_name = File.basename(element)
            if File.file?(element)
                sha_hash = Blob.create_blob(element)
                files[file_name] = sha_hash
            else
                sha_hash = Tree.build_tree(element)
                files[file_name] = sha_hash
            end
        end
        content = ""
        files.each do |file_name, sha_hash|
            content = content + file_name + NULL + sha_hash
        end
        header = "tree #{content.length}#{NULL}"
        sha_hash = get_sha_hash(header, content)
        create_object_file(header, content, sha_hash)
        return sha_hash
    end

    def self.build_working_directory(sha_hash, directory_path)
        files = Tree.get_directory_content(sha_hash)
        files.each do |file_name, sha_hash|
            if type(sha_hash).eql? "blob"
                restore_blob(sha_hash, File.join(directory_path, file_name))
            else
                Dir.mkdir(File.join(directory_path, file_name))
                build_working_directory(
                    sha_hash,
                    File.join(directory_path, file_name),
                )
            end
        end
    end

    def self.get_directory_content(sha_hash)
        input_file_path = File.join(FilePath::OBJECTS, sha_hash)
        header = nil
        files = {}
        open(input_file_path, "r") do |input_file|
            data = ""
            header, data = extract_header(input_file)
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
                    data += current_data
                end
                file_sha_hash = data[0,SHA_SIZE]
                data = data[SHA_SIZE..-1]
                files[file_name] = file_sha_hash
            end
        end
        return files
    end
end


class Commit

    def self.create_commit(commit_message, parent)
        config_parameters = {}
        open(FilePath::CONFIG, "r") do |config_file|
            while true
                data = config_file.gets
                if data.nil?
                    break
                end
                key, _separator, value = data.partition(':')
                config_parameters[key] = value
            end
        end
        header = ""
        content = ""
        content = "sha:#{Tree.build_tree(Dir.getwd)}#{EOL}"
        content += "parent:#{parent}#{EOL}"
        content += "author:#{config_parameters.fetch("author")}#{EOL}"
        content += "email:#{config_parameters.fetch("email")}#{EOL}"
        content += "time:#{Time.now}#{EOL}"
        content += "message:#{commit_message}"
        header = "commit #{content.length}#{NULL}"
        commit_hash = get_sha_hash(header, content)
        create_object_file(header, content, commit_hash)
        return commit_hash
    end

    def self.parse_commit_object(commit_hash)
        content = {}
        input_file_path = File.join(FilePath::OBJECTS, commit_hash)
        open(input_file_path, "r") do |input_file|
            data = ""
            _header, data = extract_header(input_file)
            while true
                current_data = input_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += current_data
            end
            data = data.split(EOL)
            for parameter in data
                key, _separator, value = parameter.partition(':')
                content[key] = value
            end
        end
        return content
    end
end
