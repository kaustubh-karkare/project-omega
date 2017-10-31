require 'fileutils'
require 'ostruct'
require 'tmpdir'
require 'optparse'
require './diff_utility'
require './vcs_objects'
require './exceptions'
require './vcs_internals'


class BaseCommand

    def initialize(directory_path = Dir.getwd())
        @vcs = VCS.new(directory_path)
    end

    def ensure_initialized()
        if not (
            (File.file? (@vcs.config)) &&
            (File.directory? (@vcs.objects))
        )
            raise NotVCSRepository.new('Directory not a vcs repository')
        end
    end
end


class InitCommand < BaseCommand

    # If the directory is not VCS repository then it creates one, else
    # it checks for missing directory files and reinitializes them.

    def execute(options)
        if not File.directory? (options.directory)
            FileUtils.mkdir(options.directory)
        end

        if not File.directory? (@vcs.vcs)
            FileUtils.mkdir(@vcs.vcs)
        end
        if not File.directory? (@vcs.objects)
            FileUtils.mkdir(@vcs.objects)
        end
        if not File.file? (@vcs.config)
            FileUtils.touch(@vcs.config)
            
            # The HEAD with nil indicates a dont care commit,
            # it is assumed that it doesn't contain any file.
            @vcs.set_option('HEAD', nil)
        end
        STDOUT.write("Initialized VCS repository in #{@vcs.vcs}\n")
    end
end


class StatusCommand < BaseCommand

    # Shows the changes in the working tree with respect to the last commit.

    def execute()
        ensure_initialized()
        commit_hash = @vcs.get_option('HEAD')
        if commit_hash.nil?
            STDOUT.write("No commits yet\n")
            return
        end
        status = Hash.new()
        old_directory = Dir.mktmpdir()
        begin
            commit = Commit.new(commit_hash)
            commit.restore(old_directory)
            show_status(old_directory, Dir.getwd())
        ensure
            FileUtils.remove_entry(old_directory)
        end
    end

    def show_status(old_directory, new_directory)
        hunks = DirectoryDiff.new().get_changes_in_directory(
            old_directory,
            new_directory,
        )
        hunks.each do |hunk|
            if hunk.old_file.nil?
                old_file = nil
            else
                old_file = File.basename(hunk.old_file)
            end
            if hunk.new_file.nil?
                new_file = nil
            else
                new_file = File.basename(hunk.new_file)
            end
            if old_file.nil?
                STDOUT.write("new: #{new_file}\n")
            elsif new_file.nil?
                STDOUT.write("deleted: #{old_file}\n")
            elsif (
                (File.file? (hunk.old_file)) &&
                (File.file? (hunk.new_file))
            )
                STDOUT.write("modified: #{old_file}\n")
            elsif File.file? (hunk.old_file)
                STDOUT.write("deleted: #{old_file}\n")
                new_files = FileUtilities.get_files(
                    hunk.new_file,
                    recursive = true,
                )
                new_files.each do |new_file|
                    STDOUT.write("new: #{new_file}\n")
                end
            else
                STDOUT.write("new: #{new_file}\n")
                old_files = FileUtilities.get_files(
                    hunk.old_file,
                    recursive = true,
                )
                old_files.each do |old_file|
                    STDOUT.write("deleted: #{old_file}\n")
                end
            end
        end
    end
end


class DiffCommand < BaseCommand

    # Show changes in commits or commit and working directory.

    def execute(options)
        ensure_initialized()
        diff = String.new()
        if options.old_commit.nil? && options.new_commit.nil?
            STDOUT.write("No commits yet\n")
            return
        end
        diff = String.new()
        if options.new_commit.nil?
            # The diff of the commit with the working directory
            
            old_directory = Dir.mktmpdir()
            begin
                commit = Commit.new(options.old_commit)
                commit.restore(old_directory)
                diff = DirectoryDiff.new() \
                    .generate(old_directory, Dir.getwd())
            ensure
                FileUtils.remove_entry(old_directory)
            end
        else
            old_directory = Dir.mktmpdir()
            new_directory = Dir.mktmpdir()
            begin
                old_commit = Commit.new(options.old_commit)
                if not old_commit.nil?
                    old_commit.restore(old_directory)
                end
                new_commit = Commit.new(options.new_commit)
                if not new_commit.nil?
                    new_commit.restore(new_directory)
                end
                diff = DirectoryDiff.new() \
                    .generate(old_directory, new_directory)
            ensure
                FileUtils.remove_entry(old_directory)
                FileUtils.remove_entry(new_directory)
            end
        end
        STDOUT.write(diff)
    end
end


class CommitCommand < BaseCommand

    # The commit based on the working tree is created based on
    # a commit message. File support can be introduced.

    def execute(options)
        if options.message.nil?
            raise MissingCommitParameter.new('No commit message')
        end
        ensure_initialized()
        commit_hash = Commit.create(options.message)
        @vcs.set_option('HEAD', commit_hash)
        STDOUT.write("commit #{commit_hash}\n\n#{options.message}\n\n")
    end
end


class ResetCommand < BaseCommand
    
    def execute()
        ensure_initialized()
        commit_hash = @vcs.get_option('HEAD')
        if commit_hash.nil?
            STDOUT.write("No commits yet\n")
        else
            commit = Commit.new(commit_hash)
            commit.restore(Dir.getwd())
            @vcs.set_option('HEAD', commit_hash)
            STDOUT.write("commit #{commit_hash} restored\n")
        end
    end
end


class LogCommand < BaseCommand

    # Shows the log for the commit.

    def execute(options)
        ensure_initialized()
        if options.commit_hash.nil?
            STDOUT.write("No commits yet\n")
            return
        end
        commit = Commit.new(options.commit_hash)
        STDOUT.write("commit #{options.commit_hash}\n")
        STDOUT.write(
            "Author: #{commit.get_commit('Author')} "\
            "<#{commit.get_commit('Email')}>\n"
        )
        STDOUT.write("Date: #{commit.get_commit('Date')}\n")
        STDOUT.write("\n#{commit.get_commit('Message')}\n\n")
        commit_parent = commit.get_commit('Parent')
        if not commit_parent.empty?
            options.commit_hash = commit_parent
            execute(options)
        end
    end
end


class CheckoutCommand < BaseCommand

    def execute(options)
        ensure_initialized()
        commit = Commit.new(options.commit_hash)
        commit.restore(Dir.getwd())
        @vcs.set_option('HEAD', options.commit_hash)
        STDOUT.write("Checked-out commit: #{options.commit_hash}\n")
    end
end


class ConfigCommand < BaseCommand

    def execute(options)
        ensure_initialized()
        if not options.author.nil?
            @vcs.set_option('Author', options.author)
        end
        if not options.email.nil?
            @vcs.set_option('Email', options.email)
        end
    end
end


class VCSParser

    def initialize()
        @vcs = VCS.new()
        command = ARGV.shift()

        case command
        when 'init'
            options = parse_init()
            InitCommand.new().execute(options)
        when 'status'
            StatusCommand.new().execute()
        when 'diff'
            options = parse_diff()
            DiffCommand.new().execute(options)
        when 'commit'
            options = parse_commit()
            CommitCommand.new().execute(options)
        when 'reset'
            ResetCommand.new().execute()
        when 'log'
            options = parse_log()
            LogCommand.new().execute(options)
        when 'checkout'
            options = parse_checkout()
            CheckoutCommand.new().execute(options)
        when 'config'
            options = parse_config()
            ConfigCommand.new().execute(options)
        else
            STDOUT.write("usage: vcs subcommand <options>\n")
            STDOUT.write("init\tCreate an empty vcs repository\n")
            STDOUT.write("status\tShow the working tree status\n")
            STDOUT.write(
                "diff\tShow changes between commits,"\
                "commit and working tree\n"
            )
            STDOUT.write("commit\tRecord changes to the repository\n")
            STDOUT.write("reset\tReset changes to working tree\n")
            STDOUT.write("log\tShow commit logs\n")
            STDOUT.write("checkout\tSwitch to another commit\n")
            STDOUT.write("config\tupdate repository config file\n")
            exit()
        end
    end

    def parse_init()
        options = OpenStruct.new(directory: Dir.getwd())
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs init <options>'
            opts.on(
                '-d',
                '--directory [DIRECTORY]',
                'DIRECTORY to initialize as a vcs repository',
            ) do |directory|
                options.directory = directory
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

    def parse_diff()
        options = OpenStruct.new(
            old_commit: @vcs.get_option('HEAD'),
            new_commit: nil,
        )
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs diff <options>'
            opts.on(
                '--old-commit [OLD COMMIT]',
                'OLD COMMIT for diff',
            ) do |old_commit|
                options.old_commit = old_commit
            end
            opts.on(
                '--new-commit [NEW-COMMIT]',
                'NEW COMMIT for diff',
            ) do |new_commit|
                options.new_commit = new_commit
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

    def parse_commit()
        options = OpenStruct.new(message: nil)
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs commit <options>'
            opts.on(
                '-m',
                '--message MESSAGE',
                'MESSAGE to be included in the commit',
            ) do |message|
                options.message = message
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

    def parse_log()
        options = OpenStruct.new(commit_hash: @vcs.get_option('HEAD'))
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs log <options>'
            opts.on(
                '-H',
                '--commit-hash [COMMIT HASH]',
                'COMMIT HASH to show log',
            ) do |commit_hash|
                options.commit_hash = commit_hash
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

    def parse_checkout()
        options = OpenStruct.new(commit_hash: @vcs.get_option('HEAD'))
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs checkout <options>'
            opts.on(
                '-c',
                '--commit-hash [COMMMIT HASH]',
                'COMMIT HASH to checkout',
            ) do |commit_hash|
                options.commit_hash = commit_hash
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

    def parse_config()
        options = OpenStruct.new(author: nil, email: nil)
        OptionParser.new() do |opts|
            opts.banner = 'usage: vcs checkout <options>'
            opts.on(
                '--author [AUTHOR]',
                'Author of the VCS repository',
            ) do |author|
                options.author = author
            end
            opts.on(
                '--email [EMAIL]',
                'Author EMAIL',
            ) do |email|
                options.email = email
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit()
            end
        end.order!
        return options
    end

end


VCSParser.new()
