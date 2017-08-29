require 'fileutils'
require 'tempfile'
require_relative 'file_storage'
require_relative 'diff-utility'
require_relative 'vcs_internals'


EOL = "\n"


def init(directory_path=Dir.getwd)
    if not File.directory? FilePath::VCS
        Dir.mkdir(FilePath::VCS)
        Dir.mkdir(FilePath::OBJECTS)
        open(FilePath::CONFIG, "w").close
        open(FilePath::HEAD, "w").close
    end
end


def log(commit_hash)
    commit_object_content = Commit.parse_commit_object(commit_hash)
    puts "Author: #{commit_object_content.fetch("author")}"
    puts "Author Email: #{commit_object_content.fetch("email")}"
    puts "Time: #{commit_object_content.fetch("time")}"
    puts "Message: #{commit_object_content.fetch("message")}#{EOL}#{EOL}"
    if not commit_object_content.fetch("parent").empty?
        log(commit_object_content.fetch("parent"))
    end
end


def checkout(commit_hash)
    working_directory_files = get_files_in_directory(Dir.getwd)
    commit_object_content = Commit.parse_commit_object(commit_hash)
    files_in_commit = get_files_in_tree(commit_object_content["sha"])
    files_in_commit.each do |file_name, sha|
        if working_directory_files.key? file_name
            if working_directory_files[file_name] != sha
                FileUtils.remove_entry(file_name)    
                Blob.restore_blob(sha, file_name)
            end
        else
            Blob.restore_blob(sha, file_name)
        end
    end
    working_directory_files.each do |file_name, sha|
        if not files_in_commit.key? file_name
            FileUtils.remove_entry(file_name)
        end
    end
end


def reset()
    commit_hash = File.read(FilePath::HEAD)
    checkout(commit_hash)
end


def commit(commit_message)
    commit_hash = Commit.create_commit(
        commit_message,
        parent=File.read(FilePath::HEAD)
    )
    open(FilePath::HEAD, "w") do |head_file|
        head_file.write("#{commit_hash}")
    end
    return commit_hash
end


def status(**kwargs)
    modified_files = []
    modified_files = get_modified_files(kwargs)
    if modified_files.empty?
        puts "Nothing to commit."
    else
        puts "Untracked files:#{EOL}#{EOL}"
        modified_files.each do |element|
            puts "\t#{File.basename(element.fetch(:file_name))}"
        end
    end
end


def diff(**kwargs)
    modified_files = []
    modified_files = get_modified_files(kwargs)
    modified_files.each do |element|
        puts File.basename(element.fetch(:file_name))
        original_file = nil
        modified_file = nil
        original_file = File.join(FilePath::VCS, "original_file")
        modified_file = File.join(FilePath::VCS, "modified_file")
        if element.fetch(:old_sha, nil) != nil
            original_file = Tempfile.new("original_file").path
            Blob.restore_blob(element.fetch(:old_sha), original_file)
        end
        if (
            (element.fetch(:new_sha, nil) != nil) &&
            (
                File.file? File.join(
                    FilePath::OBJECTS,
                    element.fetch(:new_sha)
                )
            )
        )
            modified_file = Tempfile.new("modified_file").path
            Blob.restore_blob(element.fetch(:new_sha), modified_file)
        else
            modified_file = element.fetch(:file_name)
        end
        find_diff(original_file, modified_file)
        puts "#{EOL}#{EOL}"
    end
end
