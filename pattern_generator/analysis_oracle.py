import os
import sys
from logzero import logger

folder_prefix = "exp-03-"
runs = 20
generators = ['qft', 'random', 'ucnot']

def precision_rate(lines):
    sec_count = 0
    for i in range(100):
        result = lines[i].strip().split(' ')[-1]
        if result == 'verified.':
            sec_count += 1
    return sec_count / 100

def get_answers(lines):
    answer_set = set()
    for i in range(100):
        answer = lines[i].strip().split(' ')[1]
        answer_set.add(answer)
    return answer_set

def get_first_satify(total_set, lines):
    idx = 0
    tmp_answer_set = set()
    while idx < 100:
        answer = lines[idx].strip().split(' ')[1]
        tmp_answer_set.add(answer)
        if tmp_answer_set == total_set:
            break
        idx += 1
    return idx

def comp_speed(list_list):
    qft_lines = open(list_list[0]).readlines()
    ucnot_lines = open(list_list[1]).readlines()
    random_lines = open(list_list[2]).readlines()
    u2_lines = open(list_list[3]).readlines()
    hs_lines = open(list_list[4]).readlines()
    qft_answers = get_answers(qft_lines)
    ucnot_answers = get_answers(ucnot_lines)
    random_answers = get_answers(random_lines)
    u2_answers = get_answers(u2_lines)
    hs_answers = get_answers(hs_lines)
    total_set = qft_answers or ucnot_answers or random_answers or u2_answers or hs_answers
    qft_first = get_first_satify(total_set, qft_lines)
    ucnot_first = get_first_satify(total_set, ucnot_lines)
    random_first = get_first_satify(total_set, random_lines)
    u2_first = get_first_satify(total_set, u2_lines)
    hs_first = get_first_satify(total_set, hs_lines)
    first_list = [
        qft_first,
        ucnot_first,
        random_first,
        u2_first,
        hs_first
    ]
    # logger.debug("qft: {}, ucnot: {}, random: {}".format(qft_first, ucnot_first, random_first))
    return first_list
        
def main():
    for run in range(runs):
        folder_name = folder_prefix + str(run).zfill(2)
        for g in generators:
            file_path = os.path.join(folder_name, g + '.random_vector_output')
            lines = open(file_path).readlines()
            pre_rate = precision_rate(lines)
            # print("Precision Rate of {}: {}".format(g, pre_rate))
            print(pre_rate, end = ' ')
            # qft random ucnot
        qft_list = os.path.join(folder_name, 'qft.random_vector_output')
        ucnot_list = os.path.join(folder_name, 'ucnot.random_vector_output')
        random_list = os.path.join(folder_name, 'random.random_vector_output')
        u2_list = os.path.join(folder_name, 'u2.random_vector_output')
        hs_list = os.path.join(folder_name, 'hs.random_vector_output')
        list_list = [
            qft_list,
            ucnot_list,
            random_list,
            u2_list,
            hs_list
        ]
        first_list = comp_speed(list_list)
        print(first_list)
        # print('qft_first: {}'.format(qft_first))
        # print('random_first: {}'.format(random_first))
        # print('ucnot_first: {}'.format(ucnot_first))

if __name__ == "__main__":
    main()