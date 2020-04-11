class Diff:

    def __init__(self):
        pass

    def run(self,file1,file2):
        file1_lines = open(file1, 'r').readlines()
        file2_lines = open(file2, 'r').readlines()

        lcs_table = self.generate_lcs_table(file1_lines, file2_lines)

        rngs = list()

        self.generate_ranges(lcs_table,file1_lines, file2_lines, len(file1_lines)-1, len(file2_lines)-1, rngs)
        rngs = rngs[::-1]
        self.merge_ranges(rngs)

        self.print_diff(file1_lines, file2_lines, rngs)


    def generate_lcs_table(self, file1_lines, file2_lines):

        lcs_table = [[0 for i in range(len(file2_lines)+1)] for j in range(len(file1_lines)+1)]

        for i in range(len(file1_lines)):
            for j in range(len(file2_lines)):
                if file1_lines[i] == file2_lines[j]:
                    lcs_table[i][j] = lcs_table[i-1][j-1] + 1
                else:
                    lcs_table[i][j] = max(lcs_table[i-1][j], lcs_table[i][j-1])

        return lcs_table

    def generate_ranges(self,lcs_table, file1_lines, file2_lines, i, j, rngs):
        if i<0 and j<0:
            return
        elif i < 0:
            new_rng = rng(i+1,i+1,j,j+1)
            rngs.append(new_rng)
            print("added i<0:", new_rng)
            self.generate_ranges(lcs_table, file1_lines, file2_lines, i, j-1, rngs)
        elif j < 0:
            new_rng = rng(i,i+1,j+1,j+1)
            rngs.append(new_rng)
            print("added j<0:", new_rng)
            self.generate_ranges(lcs_table, file1_lines, file2_lines, i-1, j,rngs)
        elif file1_lines[i] == file2_lines[j]:
            self.generate_ranges(lcs_table, file1_lines, file2_lines, i-1, j-1,rngs)
        elif lcs_table[i][j-1] >= lcs_table[i-1][j]:
            new_rng = rng(i+1,i+1,j,j+1)
            rngs.append(new_rng)
            print("added >:", new_rng)
            self.generate_ranges(lcs_table, file1_lines, file2_lines, i, j-1,rngs)
        elif lcs_table[i][j-1] < lcs_table[i-1][j]:
            new_rng = rng(i,i+1,j+1,j+1)
            rngs.append(new_rng)
            print("added <:", new_rng)
            self.generate_ranges(lcs_table, file1_lines, file2_lines, i-1, j,rngs)

    def merge_ranges(self, li):
        i = 0
        while True:
            if i >= len(li)-1:
                break
            if li[i].file_1_end == li[i+1].file_1_start:
                new_rng = rng(li[i].file_1_start, li[i+1].file_1_end, li[i].file_2_start, li[i+1].file_2_end)
                del li[i:i+2]
                li.insert(i, new_rng)
            elif li[i].file_2_end == li[i+1].file_2_start:
                new_rng = rng(li[i].file_1_start, li[i+1].file_1_end, li[i].file_2_start, li[i+1].file_2_end)
                del li[i:i+2]
                li.insert(i, new_rng)
            else: i += 1
        return li

    def print_diff(self, file1_lines, file2_lines, rngs):
        #just for individual ranges for now
        i = 0
        up_context_lines = 3
        down_context_lines = 3
        while True:
            if i >= len(rngs):
                break
            line_top = rngs[i].file_1_start
            line_bottom = rngs[i].file_2_end

            for j in range(line_top-3,line_top):
                if not j < 0:
                    print(" " + file1_lines[j], end="")

            for j in range(rngs[i].file_1_start, rngs[i].file_1_end):
                print("-" + file1_lines[j], end="")
            for j in range(rngs[i].file_2_start, rngs[i].file_2_end):
                print("+" + file2_lines[j],end="")


            for j in range(line_bottom,line_bottom+4):
                try:
                    print(" " + file2_lines[j], end="")
                except IndexError:
                    pass
            print("--------------------------------")

            i += 1
