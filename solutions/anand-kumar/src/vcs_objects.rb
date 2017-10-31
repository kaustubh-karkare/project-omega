require 'digest/sha1'
require './exceptions'
require './file_utilities'
require './vcs_internals'


BLOCK_SIZE = 1024
NULL = "\0"
SHA_SIZE = 40


class VCSObject

    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"

    attr_reader :type

    def initialize(hash)
        @vcs = VCS.new()
        if not File.file? (File.join(@vcs.objects, hash))
            raise ObjectFileError.new("#{hash} object file missing")
        end
        @hash = hash
        @type = get_type(hash)
    end

    def get_type(hash)
        content = String.new()
        type = FileUtilities.read(File.join(@vcs.objects, hash), ' ')
        case type
        when BLOB
            type = BLOB
        when TREE
            type = TREE
        when COMMIT
            type = COMMIT
        else
            raise ObjectFileError.new('Invalid object type')
        end
        return type
    end

    def ensure_type(type)
        if @type != type
            raise ObjectFileError.new('Invalid object type')
        end
    end
end


class Blob < VCSObject

    def self.create(content_file_path)
        header = "#{BLOB} #{File.size(content_file_path)}#{NULL}"
        hash = FileUtilities.get_sha1_hash(header, content_file_path)
        object_file_path = File.join(VCS.new().objects, hash)
        FileUtilities.write(object_file_path, header)
        FileUtilities.concatenate(object_file_path, content_file_path)
        return hash
    end

    def restore(output_file_path)
        object_file_path = File.join(@vcs.objects, @hash)
        header = FileUtilities.read(object_file_path, NULL)
        File.open(output_file_path, "wb").close()
        FileUtilities.concatenate(
            output_file_path,
            object_file_path,
            offset = (header + NULL).length(),
        )
    end
end


class Tree < VCSObject

    def self.create(directory_path)
        directory_content = {}
        directory_files = FileUtilities.get_files(directory_path)
        directory_files.each do |file_name|
            if File.file? (file_name)
                directory_content[file_name] = Blob.create(file_name)
            else
                directory_content[file_name] = Tree.create(file_name)
            end
        end
        content = String.new()
        directory_content.each do |file_name, hash|
            content += "#{file_name}#{NULL}#{hash}"
        end
        header = "#{TREE} #{content.length()}#{NULL}"
        hash = Digest::SHA1.hexdigest(header + content)
        FileUtilities.write(
            File.join(VCS.new().objects, hash),
            header + content,
        )
        return hash
    end

    def self.parse_object(hash)
        self.new(hash).ensure_type(TREE)
        object_file_path = File.join(VCS.new().objects, hash)
        directory_files = {}
        header = FileUtilities.read(object_file_path, NULL)
        offset = (header + NULL).length()
        while true
            file_name = FileUtilities.read(
                object_file_path,
                NULL,
                offset,
            )
            if file_name.empty?
                break
            end
            offset += (file_name + NULL).length()
            file_hash = File.read(object_file_path, SHA_SIZE, offset)
            directory_files[file_name] = file_hash
            offset += file_hash.length()
        end
        return directory_files
    end

    def restore(directory_path)
        directory_files = self.class.parse_object(@hash)
        if not File.directory? (directory_path)
            FileUtils.mkdir(directory_path)
        end

        # Removing files that are not required in the working directory.
        FileUtilities.get_files(directory_path).each do |file_path|
            if not directory_files.include? (file_path)
                FileUtils.remove_entry(file_path)
            end
        end

        # Creating and updating files in the  working directory.
        directory_files.each do |file_name, hash|
            type = get_type(hash)
            file_path = File.join(directory_path, file_name)
            case type
            when BLOB
                Blob.new(hash).restore(file_path)
            when TREE
                Tree.new(hash).restore(file_path)
            else
                raise ObjectFileError.new("#{@hash} is corrupt")
            end
        end
    end
end


class Commit < VCSObject

    def self.create(message)
        vcs = VCS.new()
        commit_parameters = {
            Author: vcs.get_option('Author'),
            Email: vcs.get_option('Email'),
            Parent: vcs.get_option('HEAD'),
            Message: message,
            Tree: Tree.create(Dir.getwd()),
            Date: Time.now().to_s,
        }
        content = String.new()
        commit_parameters.each do |key, value|
            content += "#{key.to_s}: #{value}\n"
        end
        header = "#{COMMIT} #{content.length()}#{NULL}"
        hash = Digest::SHA1.hexdigest(header + content)
        FileUtilities.write(
            File.join(vcs.objects, hash),
            header + content,
        )
        return hash
    end

    def self.parse_object(hash)
        self.new(hash).ensure_type(COMMIT)
        object_file_path = File.join(VCS.new().objects, hash)
        commit_parameters = Hash.new()
        header = FileUtilities.read(object_file_path, NULL)
        commit_data = FileUtilities.split_into_lines(
            object_file_path,
            offset = (header + NULL).length(),
        )
        commit_data.each do |parameter|
            key, _separator, value = parameter.partition(': ')
            commit_parameters[key] = value.chomp()
        end
        return commit_parameters
    end

    def get_commit(commit_key)
        commit_parameters = self.class.parse_object(@hash)
        return commit_parameters[commit_key]
    end

    def restore(directory_path = Dir.getwd())
        Tree.new(get_commit('Tree')).restore(directory_path)
    end
end
