require "./lcs"


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
        header += " @@\n"
        return header
    end
end

class DirectoryDiff

    def generate(old_directory, new_directory)
        old_files = (Dir.entries(old_directory) - ['.', '..']).sort()
        new_files = (Dir.entries(new_directory) - ['.', '..']).sort()
        diff = String.new()
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
                    diff += FileDiff.new().generate(
                        get_data(old_file),
                        get_data(new_file),
                        )
                elsif (
                    (File.directory? (old_file)) &&
                    (File.directory? (new_file))
                )
                    diff += generate(
                        File.join(old_directory, old_files[ii]),
                        File.join(new_directory, new_files[jj]),
                    )
                elsif File.directory? (old_file)
                    diff += "File #{old_file} is a directory while "\
                            "file #{new_file} is a regular file\n"
                else
                    diff += "File #{old_file} is a regular file while "\
                            "file #{new_file} is a directory\n"
                end
                ii += 1
                jj += 1
            elsif (ii < old_files.size()) && (jj < new_files.size())
                if old_files[ii] < new_files[jj]
                    diff += "Only in #{old_directory}: #{old_files[ii]}\n"
                    ii += 1
                else
                    diff += "Only in #{new_directory}: #{new_files[jj]}\n"
                    jj += 1
                end
            else
                if ii < old_files.size()
                    diff += "Only in #{old_directory}: #{old_files[ii]}\n"
                    ii += 1
                else
                    diff += "Only in #{new_directory}: #{new_files[jj]}\n" 
                    jj += 1
                end
            end
        end
        return diff
    end

    def get_data(file_path)
        data = String.new()
        File.open(file_path, "rb") do |file|
            while true
                data_block = file.read(1024)
                if data_block.nil?
                    break
                end
                data += data_block
            end
        end
        return data
    end
end
