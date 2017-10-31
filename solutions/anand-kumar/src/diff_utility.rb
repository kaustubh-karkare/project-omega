require "ostruct"
require "./file_utilities"
require "./lcs"


EOL = "\n"


class FileDiff < LongestCommonSubsequence

    @@hunk = Struct.new(:old_start, :old_end, :new_start, :new_end)
    INSERT = '+'
    DELETE = '-'
    UNCHANGED = ' '

    def generate(old_data, new_data, context_lines = 3)
        # The method generates the unified format of diff.
        
        old_data = old_data.lines()
        new_data = new_data.lines()
        hunks = get_hunks(old_data, new_data)
        hunks_with_context = add_context_around_hunks(
            hunks,
            context_lines,
            old_data.length(),
            new_data.length(),
        )
        diff = String.new()
        common_subsequence = get_lcs(old_data, new_data)
        hunks_with_context.each do |hunk_with_context|
            old_start = hunk_with_context.old_start
            old_end = hunk_with_context.old_end
            new_start = hunk_with_context.new_start
            new_end = hunk_with_context.new_end
            diff += get_context_header(hunk_with_context)
            while (old_start <= old_end) || (new_start <= new_end)
                if common_subsequence[old_start].nil?
                    diff += "#{DELETE}#{old_data[old_start - 1]}"
                    old_start += 1
                elsif common_subsequence.index(new_start).nil?
                    diff += "#{INSERT}#{new_data[new_start - 1]}"
                    new_start += 1
                else
                    diff += "#{UNCHANGED}#{old_data[old_start - 1]}"
                    old_start += 1
                    new_start += 1
                end
            end
        end
        return diff
    end

    def get_hunks(old_data, new_data)
        common_subsequence = get_lcs(old_data, new_data)
        hunks = []
        old_start = 0
        new_start = 0
        common_subsequence.each_with_index do |value, position|
            if value.nil?
                next
            end
            if (position > old_start + 1) || (value > new_start + 1)
                hunks << @@hunk.new(
                    old_start + 1,
                    position - 1,
                    new_start + 1,
                    value - 1,
                )
            end
            old_start = position
            new_start = value
        end
        return hunks
    end

    def add_context_around_hunks(
        hunks,
        context_lines,
        old_data_length,
        new_data_length
    )
        hunks_with_context = []
        
        if not hunks.any?
            return hunks_with_context
        end

        # Add context around each hunk.
        hunks.each do |hunk|
            old_start = hunk.old_start - 1
            old_end = hunk.old_end + 1
            new_start = hunk.new_start - 1
            new_end = hunk.new_end + 1

            # Context before the hunk.
            (1..context_lines).each do
                if (old_start < 1) || (new_start < 1)
                    break
                end
                hunk.old_start = old_start
                hunk.new_start = new_start
                old_start -= 1
                new_start -= 1
            end

            # Context after the hunk.
            (1..context_lines).each do
                if (old_end > old_data_length) || (new_end > new_data_length)
                    break
                end
                hunk.old_end = old_end
                hunk.new_end = new_end
                old_end += 1
                new_end += 1
            end
        end

        # Merge hunks that have overlapping context.
        hunks.each do |current_hunk|
            if hunks_with_context.any?
                previous_hunk = hunks_with_context.last()
                if (
                    (previous_hunk.old_end < current_hunk.old_start) &&
                    (previous_hunk.new_end < current_hunk.new_start)
                )
                    hunks_with_context << current_hunk
                else
                    previous_hunk.old_end = current_hunk.old_end
                    previous_hunk.new_end = current_hunk.new_end
                end
            else
                hunks_with_context << current_hunk
            end
        end
        return hunks_with_context
    end

    def get_context_header(hunk)
        old_hunk_length = hunk.old_end - hunk.old_start + 1
        new_hunk_length = hunk.new_end - hunk.new_start + 1
        header = String.new()
        header += "@@ "
        if old_hunk_length.zero?
            header += "#{DELETE}#{hunk.old_start - 1}"
        else
            header += "#{DELETE}#{hunk.old_start}"
        end
        if old_hunk_length != 1
            header += ",#{old_hunk_length}"
        end
        header += ' '
        if new_hunk_length.zero?
            header += "#{INSERT}#{hunk.new_start - 1}"
        else
            header += "#{INSERT}#{hunk.new_start}"
        end
        if new_hunk_length != 1
            header += ",#{new_hunk_length}"
        end
        header += " @@#{EOL}"
        return header
    end
end


class DirectoryDiff

    def generate(old_directory, new_directory)
        hunks = get_changes_in_directory(old_directory, new_directory)
        diff = String.new()
        hunks.each do |hunk|
            if hunk.old_file.nil?
                diff += "Only in #{new_directory}: "\
                        "#{File.basename(hunk.new_file)}#{EOL}"
            elsif hunk.new_file.nil?
                diff += "Only in #{old_directory}: "\
                        "#{File.basename(hunk.old_file)}#{EOL}"
            elsif (
                (File.file? (hunk.old_file)) &&
                (File.file? (hunk.new_file))
            )
                diff += "--- old/#{File.basename(hunk.old_file)} "\
                        "#{Time.now()}#{EOL}"
                diff += "+++ new/#{File.basename(hunk.new_file)} "\
                        "#{Time.now()}#{EOL}"
                diff += FileDiff.new().generate(
                    File.read(hunk.old_file),
                    File.read(hunk.new_file),
                )
            elsif File.file? (hunk.old_file)
                diff += "File #{hunk.old_file} is a regular file "\
                        "while file #{hunk.new_file} is a directory#{EOL}"
            else
                diff += "File #{hunk.old_file} is a directory "\
                        "while file #{hunk.new_file} is a regular file#{EOL}"
            end
        end
        return diff
    end


    def get_changes_in_directory(old_directory, new_directory)
        old_files = FileUtilities.get_files(old_directory)
        new_files = FileUtilities.get_files(new_directory)
        hunks = []
        ii = 0
        jj = 0
        while (ii < old_files.size()) || (jj < new_files.size())
            if (
                (ii < old_files.size()) &&
                (jj < new_files.size()) &&
                (old_files[ii] == new_files[jj])
            )
                old_file = File.join(old_directory, old_files[ii])
                new_file = File.join(new_directory, new_files[jj])
                if (File.file? (old_file)) && (File.file? (new_file))
                    diff = FileDiff.new().generate(
                        File.read(old_file),
                        File.read(new_file),
                    )
                    if not diff.empty?
                        hunks << modified(old_file, new_file)
                    end
                elsif (
                    (File.directory? (old_file)) &&
                    (File.directory? (new_file))
                )
                    hunks += generate(old_file, new_file)
                else
                    hunks << modified(old_file, new_file)
                end
                ii += 1
                jj += 1
            elsif (ii < old_files.size()) && (jj < new_files.size())
                if old_files[ii] < new_files[jj]
                    hunks << delete(File.join(old_directory, old_files[ii]))
                    ii += 1
                else
                    hunks << insert(File.join(new_directory, new_files[jj]))
                    jj += 1
                end
            elsif ii < old_files.size()
                hunks << delete(File.join(old_directory, old_files[ii]))
                ii += 1
            else
                hunks << insert(File.join(new_directory, new_files[jj]))
                jj += 1
            end
        end
        return hunks
    end

    def insert(file)
        return OpenStruct.new(old_file: nil, new_file: file)
    end

    def delete(file)
        return OpenStruct.new(old_file: file, new_file: nil)
    end

    def modified(old_file, new_file)
        return OpenStruct.new(old_file: old_file, new_file: new_file)
    end
end
