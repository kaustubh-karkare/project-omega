require 'fileutils'
require 'test/unit'
require 'tempfile'
require_relative 'vcs'


def temporary_directory()
    original_path = Dir.getwd
    testing_path = Dir.mktmpdir
    begin
        Dir.chdir(testing_path)
        yield
    ensure
        Dir.chdir(original_path)
        FileUtils::remove_entry(testing_path)
    end
end


def initialize_vcs_directory()
    init
    open(FilePath::CONFIG, "w") do |config_file|
        config_file.write("author: ABC\n")
        config_file.write("email: ABC@xyz.com")
    end
end


def create_temporary_file(directory_path=Dir.getwd)
    Tempfile.open("temporary_file", directory_path) do |temp_file|
        temp_file.write(Time.now)
    end
end


class VcsTest < Test::Unit::TestCase

    def test_init()
        original_path = Dir.getwd
        temporary_directory() do
            load File.join(original_path, "vcs_internals.rb")
            assert_equal false, File.directory?(FilePath::VCS)
            assert_equal false, File.directory?(FilePath::OBJECTS)
            assert_equal false, File.file?(FilePath::CONFIG)
            assert_equal false, File.file?(FilePath::HEAD)
            initialize_vcs_directory()
            assert_equal true, File.directory?(FilePath::VCS)
            assert_equal true, File.directory?(FilePath::OBJECTS)
            assert_equal true, File.file?(FilePath::CONFIG)
            assert_equal true, File.file?(FilePath::HEAD)
        end
    end

    def test_commit()
        original_path = Dir.getwd
        temporary_directory do
            load File.join(original_path, "vcs_internals.rb")
            initialize_vcs_directory()
            create_temporary_file()
            temporary_directory_path = Dir.mktmpdir
            create_temporary_file(temporary_directory_path)
            commit_hash = commit("Test commit")
            assert_equal "commit", type(commit_hash)
            files_in_directory = get_files_in_directory()
            files_in_tree = get_files_in_tree(
                Commit.parse_commit_object(commit_hash)["sha"]
            )
            assert_equal true, files_in_directory == files_in_tree
        end
    end

    def test_reset()
        original_path = Dir.getwd
        temporary_directory do
            load File.join(original_path, "vcs_internals.rb")
            initialize_vcs_directory()
            create_temporary_file()
            temporary_directory = Dir.mktmpdir
            create_temporary_file(temporary_directory)
            commit_hash = commit("First commit")
            create_temporary_file()
            reset()
            original_files = {}
            original_files = get_files_in_tree(
                Commit.parse_commit_object(commit_hash)["sha"]
            )
            updated_files = {}
            updated_files = get_files_in_directory()
            assert_equal true, original_files == updated_files
        end
    end
    
    def test_checkout()
        original_path = Dir.getwd
        temporary_directory do
            load File.join(original_path, "vcs_internals.rb")
            initialize_vcs_directory()
            create_temporary_file()
            temporary_directory = Dir.mktmpdir
            create_temporary_file(temporary_directory)
            first_commit_hash = commit("First commit")
            create_temporary_file()
            second_commit_hash = commit("Second commit")
            checkout(first_commit_hash)
            original_files = {}
            original_files = get_files_in_tree(
                Commit.parse_commit_object(first_commit_hash)["sha"]
            )
            updated_files = {}
            updated_files = get_files_in_directory()
            assert_equal true, original_files == updated_files
        end
    end

    def test_get_modified_files()
        original_path = Dir.getwd
        temporary_directory do
            load File.join(original_path, "vcs_internals.rb")
            initialize_vcs_directory()
            create_temporary_file()
            open("temporary_test_file", "w").close
            commit_hash = commit("Test commit")
            files_in_commit = get_files_in_tree(
                Commit.parse_commit_object(commit_hash)["sha"]
            )
            modified_files = {}

            # No updates
            modified_files = get_modified_files()
            assert_equal true, modified_files.empty?
            
            # New file created
            create_temporary_file
            modified_files = get_modified_files()
            assert_equal false, modified_files.empty?
            
            # File content updated
            open("temporary_test_file", "w") do |temp_file|
                temp_file.write(Time.now())
            end
            modified_files = get_modified_files()
            assert_equal false, modified_files.empty?
            checkout(commit_hash)
            
            # File deleted
            FileUtils.remove_entry("temporary_test_file")
            modified_files = get_modified_files()
            assert_equal false, modified_files.empty?
        end
    end     
end
