require 'digest/sha1'


BLOCK_SIZE = 1024
NULL = "\0"


class VcsPath

    def initialize(directory_path=Dir.getwd())
        @vcs = File.join(directory_path, ".vcs")
        @head = File.join(@vcs, "HEAD")
        @objects = File.join(@vcs, "objects")
        @config = File.join(@vcs, "config")
    end
    attr_reader :vcs, :head, :objects, :config
end


def get_sha_hash(header, path_or_content)
    sha_hash = Digest::SHA1.new
    sha_hash.update(header)
    if not path_or_content.include? NULL and File.file? path_or_content
        open(path_or_content, "rb") do |content_file|
            while true
                data = content_file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                sha_hash.update(data)
            end
        end
    else
        sha_hash.update(path_or_content)
    end
    return sha_hash.hexdigest
end


def get_files_in_directory(directory_path)
    files = {}
    for file_path in Dir.glob(File.join(directory_path, '*'))
        if File.file? file_path
            header = "blob #{File.size(file_path)}#{NULL}"
            sha_hash = get_sha_hash(header, file_path)
            files[file_path] = sha_hash
        else
            files = files.merge(get_files_in_directory(file_path))
        end
    end
    return files
end
