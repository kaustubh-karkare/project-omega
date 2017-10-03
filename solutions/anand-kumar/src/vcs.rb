require 'fileutils'
require_relative 'file_storage'


EOL = "\n"


def init(directory_path=Dir.getwd())
    vcs_path = VcsPath.new(directory_path)
    if not File.directory? vcs_path.vcs
        Dir.mkdir(vcs_path.vcs)
        Dir.mkdir(vcs_path.objects)
        open(vcs_path.config, "w").close
        open(vcs_path.head, "w").close
    end
end


def log(commit_hash)
    commit_content = Commit.new(commit_hash).get_commit_content()
    print "Author: #{commit_content.fetch("author")}#{EOL}"
    print "Author Email: #{commit_content.fetch("email")}#{EOL}"
    print "Time: #{commit_content.fetch("time")}#{EOL}"
    print "Message: #{commit_content.fetch("message")}#{EOL}#{EOL}"
    if not commit_content.fetch("parent").empty?
        log(commit_content.fetch("parent"))
    end
end


def checkout(commit_hash)
    Commit.new(commit_hash).restore(Dir.getwd())
end


def reset()
    commit_hash = File.read(VcsPath.new(Dir.getwd()).head)
    checkout(commit_hash)
end


def commit(commit_message)
    commit_hash = Commit.new().create(commit_message)
    open(VcsPath.new().head, "w") do |head_file|
        head_file.write("#{commit_hash}")
    end
    return commit_hash
end


def status()
    commit_hash = File.read(VcsPath.new().head)
    commit_tree_root = Commit.new(commit_hash).commit_tree_root
    files_in_commit = Tree.new(commit_tree_root).get_files_in_tree(Dir.getwd())
    files_in_working_directory = get_files_in_directory(Dir.getwd())
    # Modified Files
    files_in_commit.each do |file_path, file_hash|
        if (
            files_in_working_directory.key? file_path and
            files_in_working_directory[file_path] != file_hash
        )
            puts "\tmodified:\t#{File.basename(file_path)}"
        end
    end
    # Deleted Files
    files_in_commit.each do |file_path, file_hash|
        if not files_in_working_directory.key? file_path
            puts "\tdeleted:\t#{File.basename(file_path)}"
        end
    end
    # Untracked Files
    files_in_working_directory.each do |file_path, file_hash|
        if not files_in_commit.key? file_path
            puts "\tuntracked:\t#{File.basename(file_path)}"
        end
    end
end


def diff(
    old_commit=File.read(VcsPath.new().head),
    new_commit_or_path=Dir.getwd()
)
    if File.directory? new_commit_or_path
        directory_tree = Tree.new().create(new_commit_or_path)
        old_commit_tree = Commit.new(old_commit).commit_tree_root
        Tree.new(old_commit_tree).diff(directory_tree)
    else
        Commit.new(old_commit).diff(new_commit_or_path)
    end
end
