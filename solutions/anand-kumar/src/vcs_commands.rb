require 'fileutils'
require 'tmpdir'
require './diff_utility'
require './vcs_objects'
require './exceptions'
require './vcs'


class BaseCommand

    def ensure_initialized()
        vcs = VCS.new()
        if !((File.file? (vcs.config)) && (File.directory? (vcs.objects)))
            raise NotVCSRepository.new("Directory not a vcs repository")
        end
    end
end


class InitCommand < BaseCommand

    # If the directory is not VCS repository then it creates one, else
    # it checks for missing directory and files and creates them.

    def self.execute(options)
        working_directory = options[:directory]
        if not File.directory? (working_directory)
            FileUtils.mkdir(working_directory)
        end

        vcs = VCS.new(working_directory)
        if not File.directory? (vcs.vcs)
            FileUtils.mkdir(vcs.vcs)
        end
        if not File.directory? (vcs.objects)
            FileUtils.mkdir(vcs.objects)
        end
        if not File.file? (vcs.config)
            FileUtils.touch(vcs.config)
            # The HEAD with nil indicates a dont care commit,
            # it is assumed that it does not contain any file or exists.
            vcs.set_option("HEAD", nil)
        end
        STDOUT.write("Initialized VCS repository in #{vcs.vcs}\n")
    end
end


class StatusCommand < BaseCommand

    def self.execute()
        self.class.ensure_initialized()
        commit_hash = VCS.new().get_option("HEAD")
        # old_files contains the file path along with the checksum.
        if commit_hash.nil?
            old_files = {}
        else
            commit = Commit.new(commit_hash).get_commit("Tree")
            old_files = Tree.parse_object(commit.get_commit('Tree'))
        end
        
        # new_files contains the file paths in the working directory.
        new_files = FileUtilities.get_files(Dir.getwd())
        new_files.each do |new_file|
            if not old_files.include? (new_file)
                STDOUT.write("\tnew file: #{new_file}\n")
            end
        end
        old_files.each do |old_file_hash, old_file|
            if new_files.include? (old_file)
                new_file_header = "blob #{File.size(old_file)}\0"
                new_file_hash = \
                    FileUtilities.get_sha1_hash(new_file_header, file)
                if old_file_hash != new_file_hash
                    STDOUT.write("\tmodified: #{old_file}\n")
                end
            end
        end
        old_files.each do |old_file|
            if not new_files.include? (old_file)
                STDOUT.write("\tdeleted: #{old_file}\n")
            end
        end
    end
end


class DiffCommand < BaseCommand

    # diff <no-arguments>     view changes between the working directory and
    #                         the HEAD commit.
    # diff <commit> <commit>  changes between two arbitrary commits.
    # diff <commit>           changes between the working directory and
    #                         the commit.

    def self.execute(options)
        self.class.ensure_initialized()
        diff = String.new()
        if options[:new_commit].nil?
            # The diff of the commit with the working directory
            old_commit = Dir.mktmpdir()
            begin
                commit = Commit.new(options[:old_commit])
                if not commit.type? nil
                    commit.restore(old_commit)
                end
                diff = DirectoryDiff.new().generate(old_commit, Dir.getwd())
            ensure
                FileUtils.remove_entry(old_commit)
            end
        else
            old_directory = Dir.mktmpdir()
            new_directory = Dir.mktmpdir()
            begin
                old_commit = Commit.new(options[:old_commit])
                if not old_commit.nil?
                    old_commit.restore(old_directory)
                end
                new_commit = Commit.new(options[:new_commit])
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

    # The commit based on the working directory is created based on
    # a commit message. File support can be introduced.

    def self.execute(options)
        if options[:message].nil?
            raise MissingCommitMessage.new("No commit message")
        end
        self.class.ensure_initialized()
        hash = Commit.create(options[:message])
        VCS.new().set_option('HEAD', hash)
        STDOUT.write("commit #{hash} #{options[:message]} created")
    end
end


class ResetCommand < BaseCommand
    
    def self.execute()
        self.class.ensure_initialized()
        commit_hash = VCS.new().get_option('HEAD')
        if commit_hash.nil?
            STDOUT.write("No commit made in the repository\n")
        else
            commit.restore(Dir.getwd())
            VCS.new().set_option('HEAD', commit.hash)
            STDOUT.write("commit #{commit.get_commit('HEAD')} restored\n")
        end
    end
end


class LogCommand < BaseCommand

    # Shows the log for the commit.

    def self.execute(options)
        if options[:hash].nil?
            return
        end
        commit = Commit.new(options[:hash])
        STDOUT.write("commit #{options[:hash]}\n")
        STDOUT.write(
            "Author: #{commit.get_commit('Author')} "\
            "<#{commit.get_commit('Email')}>\n"
        )
        STDOUT.write("Date: commit.get_commit('Date')\n")
        STDOUT.write("\n#{commit.get_commit('Message')}\n")
        execute(options[:hash] = commit.get_commit('Parent'))
    end
end


class CheckoutCommand < BaseCommand

    def self.execute(options)
        self.class.ensure_initialized()
        commit = Commit.new(options[:hash])
        commit.restore(Dir.getwd())
        VCS.new().set_option('HEAD', commit.hash)
        STDOUT.write("Checked-out commit: #{commit.hash}\n")
    end
end


module CommandParser

    def self.init()
        options = {directory: Dir.getwd()}
        OptionParser.new() do |opts|
            opts.banner = "usage: vcs init <options>"
            opts.on(
                '-d',
                '--directory [DIRECTORY]',
                'DIRECTORY to initialize as a vcs repository',
            ) do |directory_path|
                    options[:directory] = directory_path
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit
            end
        end
        InitCommand.execute(options)
    end

    def self.status()
        StatusCommand.execute()
    end

    def self.diff()
        options = {
            old_commit: VCS.new().get_option('HEAD'),
            new_commit: nil,
        }
        OptionParser.new() do |opts|
            opts.banner = "usage: vcs diff <options>"
            opts.on(
                '--old-commit [OLD-COMMIT]',
                'OLD-COMMIT for diff',
            ) do |old_commit|
                    options[:old_commit] = old_commit
            end
            opts.on(
                '--new-commit [NEW-COMMIT]',
                'NEW-COMMIT for diff',
            ) do |new_commit|
                    options[:new_commit] = new_commit
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit
            end
        end
        DiffCommand.execute(options)
    end

    def self.commit()
        options = {message: nil}
        OptionParser.new() do |opts|
            opts.banner = "usage: vcs commit <options>"
            opts.on(
                '-m',
                '--message [MESSAGE]',
                'MESSAGE to be included in the commit',
            ) do |message|
                    options[:message] = message
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit
            end
        end
        CommitCommand.execute(options)
    end

    def self.reset()
        ResetCommand.execute()
    end

    def self.log()
        options = {hash: VCS.new().get_option('HEAD'), diff: false}
        OptionParser.new() do |opts|
            opts.banner = "usage: vcs log <options>"
            opts.on(
                '--hash [HASH]',
                'commit HASH to show log',
            ) do |hash|
                    options[:hash] = hash
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit
            end
        end
        LogCommand.execute(options)
    end

    def self.checkout()
        options = {hash: VCS.new().get_option('HEAD')}
        OptionParser.new() do |opts|
            opts.banner = "usage: vcs checkout <options>"
            opts.on(
                '-H',
                '--hash [HASH]',
                'commit HASH to checkout',
            ) do |hash|
                    options[:hash] = hash
            end
            opts.on('-h', '--help', 'Help') do
                STDOUT.write(opts)
                exit
            end
        end
        CheckoutCommand.execute(options)
    end
end
