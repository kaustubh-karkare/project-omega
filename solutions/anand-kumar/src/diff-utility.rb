class Diff

    def initialize(old_file_path, new_file_path, file_name=nil)
        @old_file_path = old_file_path
        @new_file_path = new_file_path
        @file_name = file_name
        @hunks_with_context = []
        if (@file_name.nil?)
            @file_name = @old_file_path
        end
        find_hunk_ranges()
    end

    def get_lines(file_path)
        file_lines = []
        open(file_path, "r") do |file|
            while true
                data = file.gets()
                if data.nil?
                    break
                end
                file_lines.push(data.chomp())
            end
        end
        return file_lines
    end


    def get_equivalent_lines()
        old_lines = get_lines(@old_file_path)
        new_lines = get_lines(@new_file_path)
        old_line_equivalent_in_new = Array.new(old_lines.length() + 2, 0)
        new_line_equivalent_in_old = Array.new(new_lines.length() + 2, 0)
        old_line_equivalent_in_new[old_lines.length() + 1] = \
            new_lines.length() + 1
        new_line_equivalent_in_old[new_lines.length() + 1] = \
            old_lines.length() + 1
        lcs = Array.new(old_lines.length() + 1) \
            {Array.new(new_lines.length() + 1, 0)}
        preceding_position = Array.new(old_lines.length() + 1) \
            {Array.new(new_lines.length() + 1, nil)}
        for ii in (1..old_lines.length())
            for jj in (1..new_lines.length())
                if old_lines[ii - 1] == new_lines[jj - 1]
                    lcs[ii][jj] = lcs[ii - 1][jj - 1] + 1
                    preceding_position[ii][jj] = "up-left"
                elsif lcs[ii - 1][jj] >= lcs[ii][jj - 1]
                    lcs[ii][jj] = lcs[ii - 1][jj]
                    preceding_position[ii][jj] = "up"
                else
                    lcs[ii][jj] = lcs[ii][jj - 1]
                    preceding_position[ii][jj] = "left"
                end
            end
        end
        ii = old_lines.length()
        jj = new_lines.length()
        while not preceding_position[ii][jj].nil?
            if preceding_position[ii][jj] == "up-left"
                old_line_equivalent_in_new[ii] = jj
                new_line_equivalent_in_old[jj] = ii
            end
            if preceding_position[ii][jj] == "left"
                jj -= 1
            elsif preceding_position[ii][jj] == "up"
                ii -= 1
            else
                ii -= 1
                jj -= 1
            end
        end
        return old_line_equivalent_in_new, new_line_equivalent_in_old
    end

    def find_hunk_ranges()
        old_line_equivalent_in_new, _new_line_equivalent_in_old = \
            get_equivalent_lines()
        range_start_old = 1
        range_start_new = 1
        old_line_number = 1
        while old_line_number < old_line_equivalent_in_new.length()
            if old_line_equivalent_in_new[old_line_number] != 0
                add_context_around_hunk(
                    range_start_old,
                    old_line_number,
                    range_start_new,
                    old_line_equivalent_in_new[old_line_number],
                )
                range_start_old = old_line_number + 1
                range_start_new = \
                    old_line_equivalent_in_new[old_line_number] + 1
            end
            old_line_number += 1
        end
    end

    def add_context_around_hunk(
        range_start_old,
        range_end_old,
        range_start_new,
        range_end_new,
        lines=3
    )
        total_hunks = @hunks_with_context.length()
        if (
            range_end_old - range_start_old == 0 and
            range_end_new - range_start_new == 0
        )
            return
        end
        if total_hunks == 0
            @hunks_with_context.push({
                :range_start_old=>range_start_old,
                :range_end_old=>range_end_old,
                :range_start_new=>range_start_new,
                :range_end_new=>range_end_new,
            })
            return
        end
        last_hunk = total_hunks - 1
        if (
            (
                range_start_old - @hunks_with_context[last_hunk][:range_end_old]
            ) < 2 * lines or
            (
                range_start_new - @hunks_with_context[last_hunk][:range_end_new]
            ) < 2 * lines
        )
            @hunks_with_context[last_hunk][:range_start_old] -= lines
            @hunks_with_context[last_hunk][:range_start_new] -= lines
            @hunks_with_context[last_hunk][:range_start_old] = \
                [1, @hunks_with_context[last_hunk][:range_start_old]].max
            @hunks_with_context[last_hunk][:range_start_new] = \
                [1, @hunks_with_context[last_hunk][:range_start_new]].max
            @hunks_with_context[last_hunk][:range_end_old] = range_end_old
            @hunks_with_context[last_hunk][:range_end_new] = range_end_new
        else
            @hunks_with_context[last_hunk][:range_end_old] += lines
            @hunks_with_context[last_hunk][:range_end_new] += lines
            @hunks_with_context.push({
                :range_start_old=>range_start_old - lines,
                :range_end_old=>range_end_old,
                :range_start_new=>range_start_new - lines,
                :range_end_new=>range_end_new,
            })
        end
    end

    def show(
    )
        old_line_equivalent_in_new, new_line_equivalent_in_old = \
            get_equivalent_lines()
        if @hunks_with_context.length() == 0
            return
        end
        old_lines = get_lines(@old_file_path)
        new_lines = get_lines(@new_file_path)
        puts "diff a/#{@file_name} b/#{@file_name}"
        puts "--- a/#{@file_name}"
        puts "+++ b/#{@file_name}"
        for ii in (0..@hunks_with_context.length() - 1)
            range_start_old = @hunks_with_context[ii][:range_start_old]
            range_end_old = @hunks_with_context[ii][:range_end_old]
            range_start_new = @hunks_with_context[ii][:range_start_new]
            range_end_new = @hunks_with_context[ii][:range_end_new]
            print "@@ -"
            if range_end_old - range_start_old == 0
                print "#{range_start_old + 1}"
            elsif range_end_old - range_start_old == 1
                print "#{}{range_start_old}"
            else
                print "#{range_start_old},#{range_end_old - range_start_old}"
            end
            print " +"
            if range_end_new - range_start_new == 0
                print "#{range_start_new + 1}"
            elsif range_end_new - range_start_new == 1
                print "#{range_start_new}"
            else
                print "#{range_start_new},#{range_end_new - range_start_new}"
            end
            puts " @@"
            while (
                range_start_old <= range_end_old or
                range_start_new <= range_end_new
            )
                if old_line_equivalent_in_new[range_start_old] == 0
                    puts "-#{old_lines[range_start_old - 1]}"
                    range_start_old += 1
                elsif new_line_equivalent_in_old[range_start_new] == 0
                    puts "+#{new_lines[range_start_new - 1]}"
                    range_start_new += 1
                else
                    puts " #{old_lines[range_start_old - 1]}"
                    range_start_old += 1
                    range_start_new += 1
                end
            end
        end
        print "\n"
    end
end
