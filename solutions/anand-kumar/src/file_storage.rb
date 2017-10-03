require 'fileutils'
require 'json'
require 'tempfile'
require_relative 'diff-utility'
require_relative 'vcs_internals'


SHA_SIZE = 40


class ObjectFile

    def initialize(object_hash=nil)
        @hash = object_hash
        @header = nil
        @type = nil
        if not @hash.nil?
            @header = get_current_hash_header()
            @type = %r{[a-z]+}.match(@header).to_s
        end
    end

    def create(type, path_or_content)
        if not path_or_content.include? NULL and File.file? path_or_content
            @header = "#{type} #{File.size(path_or_content)}#{NULL}"
        else
            @header = "#{type} #{path_or_content.length()}#{NULL}"
        end
        @type = type
        @hash = get_sha_hash(@header, path_or_content)
        object_file_path = File.join(VcsPath.new().objects, @hash)
        open(object_file_path, "wb") do |object_file|
            object_file.write(@header)
            if not path_or_content.include? NULL and File.file? path_or_content
                open(path_or_content, "rb") do |content_file|
                    while true
                        data = content_file.read(BLOCK_SIZE)
                        if data.nil?
                            break
                        end
                        object_file.write(data)
                    end
                end
            else
                object_file.write(path_or_content)
            end
        end
    end

    def get_current_hash_header()
        data = ""
        object_file_path = File.join(VcsPath.new().objects, @hash)
        open(object_file_path, "rb") do |object_file|
            while not data.include? NULL
                current_data = object_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += current_data
            end
        end
        header, _separator, _content = data.partition(NULL)
        return header
    end

    def restore()
        raise NotImplementedError
    end

    def diff()
        raise NotImplementedError
    end

    attr_reader :type
end


class Blob < ObjectFile

    def create(content_or_path)
        super("blob", content_or_path)
        return @hash
    end

    def restore(output_file_path)
        input_file_path = File.join(VcsPath.new().objects, @hash)
        open(input_file_path, "rb") do |input_file|
            open(output_file_path, "wb") do |output_file|
                input_file.seek((@header + NULL).length())
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

    def diff(other_blob, file_name=nil)
        old_file = Tempfile.new()
        new_file = Tempfile.new()
        if file_name.nil?
            file_name = @hash
        end
        restore(old_file.path)
        if other_blob.nil?
            # The file does not not exist anymore.
        else
            Blob.new(other_blob).restore(new_file.path)
        end
        Diff.new(old_file.path, new_file.path, file_name).show()
        old_file.close()
        new_file.close()
    end

end


class Tree < ObjectFile

    def create(directory_path)
        files = {}
        for file_path in Dir.glob(File.join(directory_path, '*'))
            file_name = File.basename(file_path)
            if File.file? file_path
                blob_hash = Blob.new().create(file_path)
                files[file_name] = blob_hash
            else
                tree_hash = Tree.new().create(file_path)
                files[file_name] = tree_hash
            end
        end
        content = ""
        files.each do |file_name, file_hash|
            content = content + file_name + NULL + file_hash
        end
        super("tree", content)
        return @hash
    end

    def get_files_from_tree_hash()
        object_file_path = File.join(VcsPath.new().objects, @hash)
        files = {}
        open(object_file_path, "rb") do |object_file|
            data = ""
            object_file.seek((@header + NULL).length())
            while true
                while not data.include? NULL
                    current_data = object_file.read(BLOCK_SIZE)
                    if current_data.nil?
                        break
                    end
                    data += current_data
                end
                if data.empty?
                    break
                end
                file_name, _separator, data = data.partition(NULL)
                while data.length() < SHA_SIZE
                    current_data = object_file.read(BLOCK_SIZE)
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

    def get_files_in_tree(directory_path)
        files_in_tree = {}
        files_in_current_directory = {}
        files_in_current_directory = get_files_from_tree_hash()
        files_in_current_directory.each do |file_name, file_hash|
            if ObjectFile.new(file_hash).type.eql? "blob"
                files_in_tree[File.join(directory_path, file_name)] = file_hash
            else
                files_in_tree = files_in_tree.merge(
                    Tree.new(file_hash).get_files_in_tree(
                        File.join(directory_path, file_name),
                    )
                )
            end
        end
        return files_in_tree
    end

    def restore(base_directory)
        working_directory_files = get_files_in_directory(base_directory)
        files_in_tree = get_files_in_tree(base_directory)
        files_in_tree.each do |file_path, file_hash|
            if working_directory_files.key? file_path
                if working_directory_files[file_path] != file_hash
                    FileUtils.remove_entry(file_path)
                    Blob.new(file_hash).restore(file_path)
                end
            else
                Blob.new(file_hash).restore(file_path)
            end
        end
        working_directory_files.each do |file_path, file_hash|
            if not files_in_tree.key? file_path
                FileUtils.remove_entry(file_path)
            end
        end
    end

    def diff(other_tree)
        old_tree_files = {}
        new_tree_files = {}
        old_tree_files = get_files_in_tree(Dir.getwd())
        new_tree_files = Tree.new(other_tree).get_files_in_tree(Dir.getwd())
        old_tree_files.each do |file_path, file_hash|
            Blob.new(file_hash).diff(new_tree_files[file_path], file_path)
        end
        new_tree_files.each do |file_path, file_hash|
            if not old_tree_files.key? file_path
                old_file = Tempfile.new()
                new_file = Tempfile.new()
                Blob.new(file_hash).restore(new_file.path)
                Diff.new(old_file.path, new_file.path, file_path).show()
                old_file.close()
                new_file.close()
            end
        end
    end
end


class Commit < ObjectFile

    def initialize(commit_hash=nil)
        super(commit_hash)
        @commit_tree_root = nil
        if not @hash.nil?
            commit_parameters = {}
            commit_parameters = get_commit_content()
            @commit_tree_root = commit_parameters.fetch("hash")
        end
    end

    def create(commit_message)
        config_parameters = {}
        open(VcsPath.new().config, "r") do |config_file|
            config_parameters = JSON.load(config_file)
        end
        @commit_tree_root = Tree.new().create(Dir.getwd())
        commit_parameters = {}
        commit_parameters[:hash] = @commit_tree_root
        commit_parameters[:parent] = File.read(VcsPath.new().head)
        commit_parameters[:author] = config_parameters.fetch("author")
        commit_parameters[:email] = config_parameters.fetch("email")
        commit_parameters[:time] = Time.now().to_s
        commit_parameters[:message] = commit_message
        header = ""
        content = ""
        commit_parameters.each do |key, value|
            content = content + key.to_s + ": " + value + EOL
        end
        super("commit", content)
        @commit_tree_root = commit_parameters[:hash]
        return @hash
    end

    def get_commit_content()
        commit_parameters = {}
        object_file_path = File.join(VcsPath.new().objects, @hash)
        open(object_file_path, "rb") do |object_file|
            data = ""
            object_file.seek((@header + NULL).length())
            while true
                current_data = object_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += current_data
            end
            data = data.split(EOL)
            for parameter in data
                key, _separator, value = parameter.partition(': ')
                commit_parameters[key] = value.chomp()
            end
        end
        return commit_parameters
    end

    def restore(base_directory)
        Tree.new(@commit_tree_root).restore(base_directory)
    end

    def diff(other_commit_hash)
        other_commit = Commit.new(other_commit_hash)
        Tree.new(@commit_tree_root).diff(other_commit.commit_tree_root)
    end

    attr_reader :commit_tree_root
end
