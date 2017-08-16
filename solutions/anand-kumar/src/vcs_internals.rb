require 'digest/sha1'


BLOCK_SIZE = 1024
NULL = "\0"
WINDOWS_LINE_END = "\r\n"
UNIX_LINE_END = "\n"


def type(sha_hash)
    file_path = File.join(Dir.getwd, ".vcs", "objects", sha_hash)
    data = ""
    open(file_path, "r") do |input_file|
        while not data.include? NULL
            current_data = input_file.read(BLOCK_SIZE)
            if current_data.nil?
                break
            end
            data += current_data
        end
    end
    header, _separator, _content = data.partition(NULL)
    return %r{[a-z]+}.match(header)
end


def get_sha_hash(header, content)
    sha1 = Digest::SHA1.new
    sha1.update(header.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
    if not content.include? NULL and File.file? content
        open(content, "r") do |content_file|
            while true
                data = content_file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                sha1.update(data.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
            end
        end
    else
        sha1.update(content.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
    end
    return sha1.hexdigest
end


def hash_object(header, content, sha_hash)
    output_path = File.join(Dir.getwd, ".vcs", "objects", sha_hash)
    open(output_path, "w") do |output_file|
        output_file.write(header.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
        if not content.include? NULL and File.file? content
            open(content, "r") do |input_file|
                while true
                    data = input_file.read(BLOCK_SIZE)
                    if data.nil?
                        break
                    end
                    output_file.write(
                        data.gsub(WINDOWS_LINE_END, UNIX_LINE_END)
                    )
                end
            end
        else
            output_file.write(content.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
        end
    end
end
