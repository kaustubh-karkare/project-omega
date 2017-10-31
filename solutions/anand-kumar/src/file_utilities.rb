require 'digest/sha1'


module FileUtilities

    BLOCK_SIZE = 1024

    def self.concatenate(file1_path, file2_path, offset = 0)
        # The content of file2 is concatenated to file1.
        
        File.open(file1_path, 'ab') do |file1|
            File.open(file2_path, 'rb') do |file2|
                file2.seek(offset)
                while true
                    data = file2.read(BLOCK_SIZE)
                    if data.nil?
                        break
                    end
                    file1.write(data)
                end
            end
        end
    end

    def self.read(file_path, delimiter = '\n', offset = 0)
        # The method returns the file content before the delimiter
        # is encountered, if the delimiter (default: new line) is not present
        # then it returns the entire content available.

        content = String.new()
        File.open(file_path, 'rb') do |file|
            file.seek(offset)
            while not content.include? delimiter
                data = file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                content += data
            end
        end
        content, _separator, _data = content.partition(delimiter)
        return content
    end
    
    def self.split_into_lines(file_path, offset = 0)
        lines = []
        File.open(file_path, 'rb') do |file|
            file.seek(offset)
            while true
                data = file.gets()
                if data.nil?
                    break
                end
                lines << data
            end
        end
        return lines
    end

    def self.write(file_path, data, mode = 'wb')
        File.open(file_path, mode) {|file| file.write(data)}
    end

    def self.get_sha1_hash(header, file_path)
        hash = Digest::SHA1.new()
        hash.update(header)
        open(file_path, 'rb') do |file|
            while true
                data = file.read(BLOCK_SIZE)
                if data.nil?
                    break
                end
                hash.update(data)
            end
        end
        return hash.hexdigest
    end

    def self.get_files(directory_path = Dir.getwd(), recursive = false)
        # Returns the list of file paths, dot files are ignored.

        files = []
        original_path = Dir.getwd()
        begin
            Dir.chdir(directory_path)
            if recursive
                files = Dir["*/*"] - ['.', '..']
            else
                files = Dir["*"] - ['.', '..']
            end
        ensure
            Dir.chdir(original_path)
        end
        return files
    end
end
