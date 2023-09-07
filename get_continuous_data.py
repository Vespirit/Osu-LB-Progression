from typing import List, Tuple
from get_snapshots import only_digits

def num_ranks_in_line(line: list[str]) -> int:
    return (len(line) - 1) // 2

def id_exists(id: str, line: list[str]) -> int:

    for i in range(num_ranks_in_line(line)):

        if line[i*2+1] == id:
            return i
    return -1

def get_new_pp(start_pp, end_pp, start_day, end_day, cur_day):
    left_bias = cur_day - start_day
    day_difference = end_day - start_day
    p = left_bias / day_difference
    pp_difference = end_pp - start_pp

    pp_left_bias = p * pp_difference
    return int(start_pp + pp_left_bias)

def player_pp_on_day(id: str, day: int, csv_data: List[str], start_line_num: int, end_line_num: int) -> int:
    '''
    day must be within the range of days spanned by start_line_num and end_line_num
    '''
    print(start_line_num, " ", end_line_num, " ", id, " ", day)
    for i in range(start_line_num, end_line_num + 1):
        cur_line = csv_data[i].split(',')
        cur_day = int(cur_line[0])

        rank = id_exists(id, cur_line)

        if rank >= 0:
            if cur_day == day:
                return int(cur_line[rank * 2 + 2])
            
            elif cur_day > day:
                end_line_num = i
                break

            else:
                start_line_num = i

    start_line = csv_data[start_line_num].split(",")
    end_line = csv_data[end_line_num].split(",")

    start_rank = id_exists(id, start_line)
    end_rank = id_exists(id, end_line)

    if start_rank < 0:
        start_pp = int(start_line[-1])
    else:
        start_pp = int(start_line[start_rank * 2 + 2])

    if end_rank < 0:
        end_pp = int(start_line[-1])
    else:
        end_pp = int(end_line[end_rank * 2 + 2])

    start_day = int(start_line[0])
    end_day = int(end_line[0])

    return get_new_pp(start_pp, end_pp, start_day, end_day, day)

def sort_pair(id_pp_pairs: List[Tuple[str, int]]) -> None:

    for i in range(len(id_pp_pairs)):

        max_idx = i
        for j in range(i+1, len(id_pp_pairs)):
            if id_pp_pairs[max_idx][1] < id_pp_pairs[j][1]:
                max_idx = j

        id_pp_pairs[i], id_pp_pairs[max_idx] = id_pp_pairs[max_idx], id_pp_pairs[i]


def make_continuous(csv_file: str, new_file: str) -> None:

    with open(csv_file, "r") as f_csv:
        csv_data = f_csv.readlines()
    
    with open(new_file, "w") as f_new:
        i = 0
        while i < len(csv_data) - 1:
            print(i)
            start_line_num = i
            end_line_num = i+1

            end_line = csv_data[end_line_num].split(",")
            while num_ranks_in_line(end_line) < 50:
                end_line_num += 1
                end_line = csv_data[end_line_num].split(",")

            ids = []

            start_day = int(csv_data[start_line_num].split(",")[0])
            end_day = int(end_line[0])

            for j in range(start_line_num, end_line_num + 1):
                cur_line = csv_data[j].split(',')
                for rank in range(num_ranks_in_line(cur_line)):

                    id = cur_line[rank * 2 + 1]
                    if id not in ids:
                        ids.append(id)

            for j in range(start_day, end_day):

                id_pp_pairs = []

                for id in ids:
                    pp = player_pp_on_day(id, j, csv_data, start_line_num, end_line_num)
                    id_pp_pairs.append((id, pp))

                sort_pair(id_pp_pairs)

                f_new.write(str(j))

                for pair in id_pp_pairs[:50]:
                    f_new.write("," + pair[0] + "," + str(pair[1]))

                f_new.write('\n')
            
            i = end_line_num

        f_new.write(csv_data[-1])

if __name__ == '__main__':
    make_continuous("data/lb_data.csv", "data/lb_continuous.csv")