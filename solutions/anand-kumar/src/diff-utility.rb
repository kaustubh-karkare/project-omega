require_relative 'vcs_internals'


NodeValue = Struct.new(:key, :parent_x, :parent_y)


def get_lcs(old_lines, new_lines)
    lcs = Array.new(old_lines.length + 1) \
        {Array.new(new_lines.length + 1, NodeValue.new(0, 0, 0))}
    for ii in (1..old_lines.length)
        for jj in (1..new_lines.length)
            if old_lines[ii - 1] == new_lines[jj - 1]
                lcs[ii][jj] = NodeValue.new(
                    lcs[ii - 1][jj - 1].key + 1,
                    ii - 1,
                    jj - 1
                )
            else
                lcs[ii][jj] = NodeValue.new(lcs[ii][jj - 1].key, ii, jj - 1)
                if lcs[ii - 1][jj].key > lcs[ii][jj].key
                    lcs[ii][jj].key = lcs[ii - 1][jj].key
                    lcs[ii][jj].parent_x = ii - 1
                    lcs[ii][jj].parent_y = jj
                end
            end
        end
    end
    lcs_old = Array.new(old_lines.length + 1, 0)
    lcs_new = Array.new(new_lines.length + 1, 0)
    current_x = old_lines.length
    current_y = new_lines.length
    while current_x != 0 || current_y != 0
        parent_x = lcs[current_x][current_y].parent_x
        parent_y = lcs[current_x][current_y].parent_y
        if current_x - 1 == parent_x && current_y - 1 == parent_y
            lcs_old[current_x] = current_y
            lcs_new[current_y] = current_x
        end
        current_x = parent_x
        current_y = parent_y
    end
    return lcs_old, lcs_new
end


def display_diff_delete(lines, lcs, index, line_new)
    start_index = index
    end_index = index
    index += 1
    while index <= lines.length && lcs[index] == 0 
        end_index += 1
        index += 1
    end
    if start_index == end_index
        puts "#{start_index}d#{line_new}"
        puts "< #{lines[start_index - 1]}"
    else
        puts "#{start_index},#{end_index}d#{line_new}"
        while start_index <= end_index
            puts "< #{lines[start_index - 1]}"
            start_index += 1
        end
    end
    return index
end


def display_diff_append(lines, lcs, index, line_old, line_new)
    line_new += 1
    start_index = index
    end_index = index
    index += 1
    while index <= lines.length && lcs[index] == 0
        index += 1
        end_index += 1
    end
    if start_index == end_index    
        puts "#{line_old}a#{line_new}"
        puts "> #{lines[start_index - 1]}"
    else
        puts "#{line_old}a#{line_new},#{line_new + (end_index - start_index)}"
        line_new  += (end_index - start_index)
        while start_index <= end_index
            puts "> #{lines[start_index - 1]}"
            start_index += 1
        end
    end
    return index, line_new
end


def display_diff_change(
    old_lines,
    new_lines,
    lcs_old,
    lcs_new,
    start_old_index,
    start_new_index,
    line_new
)
    line_new += 1
    start_old = start_old_index
    start_new = start_new_index
    end_old = start_old_index
    end_new = start_new_index

    start_old_index += 1
    start_new_index += 1
    while (
        start_old_index <= old_lines.length &&
        start_new_index <= new_lines.length &&
        lcs_old[start_old_index] == 0 &&
        lcs_new[start_new_index] == 0
    )
        start_old_index += 1
        end_old += 1
        start_new_index += 1
        end_new += 1
    end
    if start_old == end_old
        puts "#{start_old}c#{line_new}"
        puts "< #{old_lines[start_old - 1]}"
        puts "---"
        puts "> #{new_lines[start_new - 1]}"
    else
        print "#{start_old},#{end_old}c#{line_new},"
        print "#{line_new + (end_old - start_old)}\n"
        line_new += (end_old - start_old)
        while start_old <= end_old
            puts "< #{old_lines[start_old - 1]}"
            start_old += 1
        end
        puts "---"
        while start_new <= end_new
            puts "> #{new_lines[start_new - 1]}"
            start_new += 1
        end
    end
    return start_old_index, start_new_index, line_new
end


def find_diff(file1, file2)
    old_lines = []
    new_lines = []
    if File.file?(file1)
        open(file1, "r") do |old_file|
            while true
                data = old_file.gets
                if data.nil?
                    break
                end
                old_lines.push(data)
            end
        end
    else
        old_lines.push(file1)
    end
    if File.file?(file2)
        open(file2, "r") do |new_file|
            while true
                data = new_file.gets
                if data.nil?
                    break
                end
                new_lines.push(data)
            end
        end
    else
        new_lines.push(file2)
    end
    lcs_old, lcs_new = get_lcs(old_lines, new_lines)
    line_number_new = 0
    old_index = 1
    new_index = 1
    while old_index <= old_lines.length || new_index <= new_lines.length
        if (
            lcs_old[old_index] == 0 &&
            (new_index > new_lines.length || lcs_new[new_index] != 0)
        )
            old_index = display_diff_delete(
                old_lines,
                lcs_old,
                old_index,
                line_number_new
            )
        elsif (
            lcs_new[new_index] == 0 &&
            (old_index > old_lines.length || lcs_old[old_index] != 0)
        )
            new_index, line_number_new = display_diff_append(
                new_lines,
                lcs_new,
                new_index,
                old_index - 1,
                line_number_new
            )
        elsif lcs_old[old_index] == 0 && lcs_new[new_index] == 0
            old_index, new_index, line_number_new = display_diff_change(
                old_lines,
                new_lines,
                lcs_old,
                lcs_new,
                old_index,
                new_index,
                line_number_new
            )
        else lcs_new[new_index] == old_index
            line_number_new += 1
            old_index += 1
            new_index += 1
        end
    end    
end
