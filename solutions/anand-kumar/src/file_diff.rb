require './lcs'


class FileDiff < LongestCommonSubsequence

    @@hunk = Struct.new(:old_start, :old_end, :new_start, :new_end)

    def generate(old_data, new_data, context_lines = 3)
        # The method generates the unified format of diff.
        
        hunks = get_hunks(old_data, new_data)
        hunks_with_context = add_context_around_hunks(
            hunks,
            context_lines,
            old_data.size(),
            new_data.size(),
        )
        diff = []
        common_subsequence = get_lcs(old_data, new_data)
        hunks_with_context.each do |hunk_with_context|
            old_start = hunk_with_context.old_start
            old_end = hunk_with_context.old_end
            new_start = hunk_with_context.new_start
            new_end = hunk_with_context.new_end
            diff << get_context_header(hunk_with_context)
            while (old_start <= old_end) || (new_start <= new_end)
                if common_subsequence[old_start].nil?
                    diff << "-#{old_data[old_start - 1]}"
                    old_start += 1
                elsif common_subsequence.index(new_start).nil?
                    diff << "+#{new_data[new_start - 1]}"
                    new_start += 1
                else
                    diff << " #{old_data[old_start - 1]}"
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
        old_data_size,
        new_data_size
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
                if (old_end > old_data_size) || (new_end > new_data_size)
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
        header = ""
        header << "@@ "
        if old_hunk_length.zero?
            header << "-#{hunk.old_start - 1}"
        else
            header << "-#{hunk.old_start}"
        end
        if old_hunk_length != 1
            header << ",#{old_hunk_length}"
        end
        if new_hunk_length.zero?
            header << " +#{hunk.new_start - 1}"
        else
            header << " +#{hunk.new_start}"
        end
        if new_hunk_length != 1
            header << ",#{new_hunk_length}"
        end
        header << " @@"
        return header
    end

    def apply_diff(old_data, diff)
        old_data_index = nil
        deletions = 0
        insertions = 0
        diff.each do |line|
            header = /
                ^
                @@\s
                -(?<old_start>\d)
                (?:,(?<old_data_length>\d))?
                \s
                \+(?<new_start>\d)
                (?<new_data_length>(?:,\d))?
                \s@@
            $/x.match(line)
            if !header.nil?
                old_data_index = header[:old_start].to_i
                if (
                    !header[:old_data_length].nil? &&
                    header[:old_data_length].to_i.zero?
                )
                    old_data_index += 1
                end
                old_data_index = old_data_index - deletions + insertions
            else
                command = /^(?<operation>[-\s\+])(?<data>.*)/.match(line)
                case command[:operation]
                when '-'
                    old_data.delete_at(old_data_index - 1)
                    deletions += 1
                when '+'
                    old_data.insert(old_data_index - 1, command[:data])
                    insertions += 1
                    old_data_index += 1
                else
                    old_data_index += 1
                end
            end
        end
        return old_data
    end
end
