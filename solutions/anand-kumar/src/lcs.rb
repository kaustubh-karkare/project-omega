class LongestCommonSubsequence

    @@candidate = Struct.new(:x_position, :y_position, :previous)

    def get_lcs(x, y)
        # The method uses Hunt-Mcilroys solution to the longest common
        # subsequence problem and returns an array 'common_subsequence' such
        # that for an element at any position (0..x.size()) in x,
        # common_subsequence[position] is the position of the element in y.

        common_subsequence = []
        x_start = 0
        x_finish = x.size() - 1
        y_start = 0
        y_finish = y.size() - 1

        # Skip the identical sequence from the start.
        while (
            (x_start <= x_finish) and
            (y_start <= y_finish) and
            (x[x_start] == y[y_start])
        )
            common_subsequence[x_start + 1] = y_start + 1
            x_start += 1
            y_start += 1
        end

        # Skip the identical sequence from the end.
        while (
            (x_start <= x_finish) and
            (y_start <= y_finish) and
            (x[x_finish] == y[y_finish])
        )
            common_subsequence[x_finish + 1] = y_finish + 1
            x_finish -= 1
            y_finish -= 1
        end

        # The equivalence_class is a hash such that its key is an element of
        # the sequence and the corresponding value is an array storing the
        # position(s) of the element in the sequence.

        equivalence_class = Hash.new{|key, value| key[value] = []}
        (y_start..y_finish).each do |ii|
            equivalence_class[y[ii]] << ii
        end

        # The kth_candidates stores the reference to a k-candidate object
        # such that for a k-candidate(ii, jj):
        # i)   x[ii] == y[jj]
        # ii)  a k length common subsequence exists between the first ii
        #      elements of sequence x and first jj elements of sequence y, and
        # iii) no k length common subsequence exist if either ii or jj
        #      is reduced.

        kth_candidates = []
        kth_candidates << @@candidate.new(0, 0, nil)
        kth_candidates << @@candidate.new(x_finish + 1, y_finish + 1, nil)
        (x_start..x_finish).each do |ii|
            update_kth_candidates(
                kth_candidates,
                equivalence_class[x[ii]],
                ii,
            )
        end
        candidate = kth_candidates[kth_candidates.size() - 2]
        while not candidate.nil?
            common_subsequence[candidate.x_position] = candidate.y_position
            candidate = candidate.previous
        end
        common_subsequence[x.size() + 1] = y.size() + 1
        return common_subsequence
    end

    def update_kth_candidates(kth_candidates, identical_lines, ii)
        kth_start = 0
        kth_end = kth_candidates.size() - 2
        start_candidate = kth_candidates[kth_start]
        identical_lines.each do |jj|
            candidate_position = get_candidate_position(
                kth_candidates,
                kth_start,
                kth_end,
                jj + 1,
            )
            if candidate_position != -1
                if candidate_position == kth_end
                    kth_candidates[kth_end + 2] = kth_candidates[kth_end + 1]
                end
                parent_candidate = kth_candidates[candidate_position]
                kth_candidates[kth_start] = start_candidate
                start_candidate = @@candidate.new(
                    ii + 1,
                    jj + 1,
                    parent_candidate,
                )
                kth_start = candidate_position + 1
            end
        end
        kth_candidates[kth_start] = start_candidate
    end

    def get_candidate_position(candidates, start, finish, value)
        # Binary search to find the k-candidate position such that:
        #   candidates[position].y_position < value and
        #   candidates[position + 1].y_position > value

        if start <= finish
            mid = (start + finish) >> 1
            if candidates[mid].y_position < value
                return [
                    mid,
                    get_candidate_position(
                        candidates,
                        mid + 1,
                        finish,
                        value,
                    )
                ].max()
            else
                return get_candidate_position(
                    candidates,
                    start,
                    mid - 1,
                    value,
                )
            end
        end
        return -1
    end
end
