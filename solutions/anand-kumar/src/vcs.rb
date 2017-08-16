require_relative 'commit'
require_relative 'diff_utility'
require_relative 'tree'


EOL = "\n"


def init(directory_path=Dir.getwd)
    if not File.directory?(File.join(directory_path, ".vcs"))
        Dir.mkdir(File.join(directory_path, ".vcs"))
        Dir.chdir(File.join(directory_path, ".vcs"))
        Dir.mkdir("objects")
        open("config", "w").close
        open("HEAD", "w").close
        Dir.chdir(directory_path)
    end
end


def log(commit_hash)
    content = parse_commit_object(commit_hash)
    puts "Author: #{content.fetch("author")}"
    puts "Author Email: #{content.fetch("email")}"
    puts "Time: #{content.fetch("time")}"
    puts "Message: #{content.fetch("message")}#{EOL}"
    if not content.fetch("parent").empty?
        commit_log(content.fetch("parent"))
    end
end


def checkout(commit_hash)
    delete_working_directory(Dir.getwd)
    content = parse_commit_object(commit_hash)
    build_working_directory(content.fetch("sha"), Dir.getwd)
end


def reset()
    commit_hash = File.read(File.join(Dir.getwd, ".vcs", "HEAD"))
    checkout(commit_hash)
end


def commit(commit_message)
    head_path = File.join(Dir.getwd, ".vcs", "HEAD")
    parent = File.read(head_path)
    head = create_commit(commit_message, parent)
    open(head_path, "w") do |head_file|
        head_file.write("#{head}")
    end
    return head
end


def status()
    modified_files = {}
    modified_files = get_modified_files()
    if modified_files.length == 0
        puts "Nothing to commit."
    else
        puts "Untracked files:#{EOL}#{EOL}"
        modified_files.each do |file_name, sha_hash|
            puts "\t#{File.basename(file_name)}"
        end
    end
end


def diff()
    head = File.join(Dir.getwd, ".vcs", "HEAD")
    files_in_previous_commit = {}
    files_in_previous_commit = get_files_from_commit(
        parse_commit_object(File.read(head)).fetch("sha"),
        Dir.getwd
    )
    modified_files = {}
    modified_files = get_modified_files()
    modified_files.each do |modified_file, modified_file_sha|
        puts File.basename(modified_file)
        original_file = File.join(Dir.getwd, ".vcs", "temporary_file")
        open(original_file, "w").close
        if files_in_previous_commit.key? modified_file
            restore_blob(
                files_in_previous_commit[modified_file],
                original_file
            )
        end
            find_diff(original_file, modified_file)
        File.delete(original_file)
        puts "#{EOL}#{EOL}"
    end
end
