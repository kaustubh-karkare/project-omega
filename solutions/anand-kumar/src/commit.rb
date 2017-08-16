require_relative 'tree'
require_relative 'vcs_internals'


def create_commit(commit_message, parent)
    config_file_path = File.join(Dir.getwd, ".vcs", "config")
    config_parameters = {}
    open(config_file_path, "r") do |config_file|
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
    content = "sha:#{build_tree(Dir.getwd)}#{NULL}"
    content += "parent:#{parent}#{NULL}"
    content += "author:#{config_parameters.fetch("author")}#{NULL}"
    content += "email:#{config_parameters.fetch("author-email")}#{NULL}"
    content += "time:#{Time.now}#{NULL}"
    content += "message:#{commit_message}"
    header = "commit #{content.length}#{NULL}"
    commit_hash = get_sha_hash(header, content)
    hash_object(header, content, commit_hash)
    return commit_hash
end


def parse_commit_object(commit_hash)
    content = {}
    input_file_path = File.join(Dir.getwd, ".vcs", "objects", commit_hash)
    open(input_file_path, "r") do |input_file|
        data = ""
        while not data.include? NULL
            current_data = input_file.read(BLOCK_SIZE)
            if current_data.nil?
                break
            end
            data += current_data
        end
        _header, _separator, data = data.partition(NULL)
        while true
            current_data = input_file.read(BLOCK_SIZE)
            if current_data.nil?
                break
            end
            data += current_data
        end
        data = data.split(NULL)
        for parameter in data
            key, _separator, value = parameter.partition(':')
            content[key] = value
        end
    end
    return content
end


def get_files_from_commit(sha_hash, directory_path)
    files_in_commit = {}
    files_in_current_node = {}
    files_in_current_node = get_directory_content(sha_hash)
    files_in_current_node.each do |file_name, sha_hash|
        if type(sha_hash).to_s.eql?("blob")
            files_in_commit[File.join(directory_path, file_name)] = \
                sha_hash
        else
            files_in_commit.merge(
                get_files_from_commit(
                    sha_hash,
                    File.join(directory_path, file_name)
                )
            )
        end
    end
    return files_in_commit
end
