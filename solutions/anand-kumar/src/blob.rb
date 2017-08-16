require_relative 'vcs_internals'


def create_blob(content)
    header = "blob #{File.size(content)}#{NULL}"
    sha_hash = get_sha_hash(header, content)
    hash_object(header, content, sha_hash)
    return sha_hash
end


def restore_blob(sha_hash, output_file_path)
    input_file_path = File.join(Dir.getwd, ".vcs", "objects", sha_hash)
    open(input_file_path, "r") do |input_file|
        open(output_file_path, "w") do |output_file|
            data = ""
            while not data.include? NULL
                current_data = input_file.read(BLOCK_SIZE)
                if current_data.nil?
                    break
                end
                data += current_data
            end
            _header, _separator, data = data.partition(NULL)
            output_file.write(data.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
            while true
                data = input_file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                output_file.write(data.gsub(WINDOWS_LINE_END, UNIX_LINE_END))
            end
        end
    end
end
