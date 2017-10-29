require 'digest/sha1'
require 'optparse'
require './exceptions'
require './file_utilities'
require './vcs'


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
            raise ObjectFileError.new("Invalid object type")
        end
        return type
    end

    def ensure_type(type)
        if @type != type
            raise ObjectFileError.new('Object type not matching with class')
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
        Dir.foreach(directory_path) do |file_name|
            if ['.', '..'].include? (file_name)
                next
            end
            if File.file? (file_name)
                directory_content[file_name] = \
                    Blob.create(File.join(directory_path, file_name))
            else
                directory_content[file_name] = \
                    Tree.create(File.join(directory_path, file_name))
            end
        end
        content = String.new()
        directory_content.each do |file_name, hash|
            content += "#{file_name} #{NULL}#{hash}"
        end
        header = "#{TREE} #{content.length()}#{NULL}"
        hash = Digest::SHA1.new(header + content).hexdigest
        FileUtilities.write(
            File.join(VCS.new().objects, hash),
            header + content,
        )
        return hash
    end

    def self.parse_object(hash)
        self.class.ensure_type(TREE)
        object_file_path = File.join(@vcs.objects, hash)
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
            File.open(object_file_path, "rb") {
                |file|  hash = file.read(SHA_SIZE, offset)
            }
            directory_files[file_name] = hash
            offset += hash.length()
        end
        return directory_files
    end

    def restore(directory_path)
        directory_files = self.class.parse_object(@hash)
        if not File.directory? (directory_path)
            FileUtils.mkdir(directory_path)
        end

        # Creating and updating files in the  working directory.
        directory_files.each do |file_name, hash|
            type = get_type(hash)
            file_path = File.join(directory_path, file_name)
            if type == BLOB
                Blob.new(hash).restore(file_path)
            elsif type == TREE
                Tree.new(hash).restore(file_path)
            else
                raise ObjectFileError.new("#{@hash} is corrupt")
            end
        end

        # Removing files that do not belong in the working directory.
        Dir.foreach(directory_path) do |file_name|
            if ['.', '..'].include? (file_name)
                next
            end
            if not directory_files.include? (file_name)
                if File.file? (file_name)
                    FileUtils.rm(file_name)
                else
                    FileUtils.rm_r(file_name)
                end
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
        hash = Digest::SHA1.new(header + content).hexdigest
        FileUtilities.write(
            File.join(vcs.objects, hash),
            header + content,
        )
        return hash
    end

    def self.parse_object(hash)
        self.class.ensure_type(COMMIT)
        object_file_path = File.join(@vcs.config, hash)
        commit_parameters = Hash.new()
        header = FileUtilities.read(object_file_path, NULL)
        offset = (header + NULL).length()
        while true
            parameter = FileUtilities.read(
                object_file_path,
                NULL,
                offset,
            )
            if parameter.empty?
                break
            end
            key, _separator, value = parameter.partition(": ")
            commit_parameters[key] = value
            offset += parameter
        end
        return commit_parameters
    end

    def get_commit(commit_key)
        commit_parameters = self.class.parse_object(@hash)
        return commit_parameters[commit_key]
    end

    def restore()
        Tree.new(get_commit('Tree')).restore(Dir.getwd())
    end
end
