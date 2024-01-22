import os
import sys
import numpy as np
from logzero import logger

folder_prefix = "exp-01-"

generators = [
    'QFTMutator',
    'RandomMutator',
    'UCNOTMutator'
]

def mag_analysis(content, num_qubits):
    all_state_num = pow(2, num_qubits)
    freq_every_state = (1 / all_state_num) * 10000
    standard_deviation = 0
    for k, e in content.items():
        tmp = pow(e - freq_every_state, 2)
        standard_deviation += tmp
    standard_deviation /= all_state_num
    standard_deviation = np.sqrt(standard_deviation)
    return standard_deviation

def skip_bit(strs, idx):
    if idx == 0:
        return strs[1:]
    elif idx == len(strs) - 1:
        return strs[:idx]
    else:
        return strs[:idx] + strs[idx+1:]
    
def gen_bin_dict(num_qubits):
    output_list = list()
    output_list.append("0" * num_qubits)
    for i in range(1, pow(2, num_qubits)):
        tmp = list()
        r = 0
        while (i!=0):
            r = i%2
            i = i//2
            tmp = [str(r)] + tmp
        output_list.append("".join(tmp).zfill(num_qubits))
    output_dict = dict()
    for k in output_list:
        output_dict[k] = 0
    return output_dict

def entangle_analysis(content, num_qubits):
    all_states_num_minus = pow(2, num_qubits - 1)
    rate_of_dist = list()
    for lock_bit_idx in range(num_qubits):
        bin_dict_minus = gen_bin_dict(num_qubits - 1)
        ob_bar_count = 0
        for k, e in content.items():
            rest_bits = skip_bit(k, lock_bit_idx)
            bin_dict_minus[rest_bits] += e
        for k, e in bin_dict_minus.items():
            if e > 0:
                ob_bar_count += 1
        rate = np.around(ob_bar_count / all_states_num_minus, decimals = 3)
        rate_of_dist.append(rate)
    return max(rate_of_dist)

def analysis(result_path, num_qubits):
    content = eval(open(result_path).read())
    mag_score = mag_analysis(content, num_qubits)
    entangle_score = entangle_analysis(content, num_qubits)
    # logger.debug("now analysis {0}, mag score: {1:.2f}, entagnle score: {2:.2f}".format(result_path, mag_score, entangle_score))
    return mag_score, entangle_score

def main():
    for i in range(3, 11):
        folder_name = folder_prefix + str(i).zfill(2)
        for g in generators:
            sum_mag_score = 0
            sum_eng_score = 0
            for run in range(100):
                second_folder = 'run_' + str(run).zfill(2)
                result_path = os.path.join(folder_name, second_folder, g, 'results')
                mag_score, entangle_score = analysis(result_path, i)
                sum_mag_score += mag_score
                sum_eng_score += entangle_score
            avg_mag_score = sum_mag_score / 100
            avg_eng_score = sum_eng_score / 100
            logger.debug("{0} in {1} qubits, avg mag: {2:.2f}, avg eng: {3:.2f}".format(g, i, avg_mag_score, avg_eng_score))

if __name__ == "__main__":
    main()