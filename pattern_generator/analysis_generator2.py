import os
import sys
from logzero import logger
from mutator import RandomMutator, QFTMutator, UCNOTMutator
from line import Circuit
from copy import deepcopy
import math
import numpy as np
import csv

mutators = {
    "random": RandomMutator(),
    "qft": QFTMutator(),
    "ucnot": UCNOTMutator()
}

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

def skip_bit(strs, idx):
    if idx == 0:
        return strs[1:]
    elif idx == len(strs) - 1:
        return strs[:idx]
    else:
        return strs[:idx] + strs[idx+1:]

def dec_to_bin(strs):
    return format(int(strs), 'b')

def phase_analysis(num_qubits, phase_result):
    qubit_list = list()
    bin_dict = gen_bin_dict(num_qubits)
    for i in range(pow(2, num_qubits)):
        bins = dec_to_bin(str(i)).zfill(num_qubits)
        bin_dict[bins] = (phase_result[i].real, phase_result[i].imag)
    bin_phase_dict = gen_bin_dict(num_qubits)
    for k, v in bin_dict.items():
        real, imag = v
        mean_real = real/math.sqrt(real**2 + imag**2)
        mean_imag = imag/math.sqrt(real**2 + imag**2)
        phase = math.atan2(mean_imag, mean_real)
        phase_angle = (phase * 180) / 3.142
        bin_phase_dict[k] = phase_angle + 180
    # sub_list = []
    # bin_dict_minus = gen_bin_dict(num_qubits - 1)
    # ob_bar_count = 0
    
    # for k, e in bin_phase_dict.items():
    #     rest_bits = skip_bit(k, lock_bit_idx)
    #     bin_dict_minus[rest_bits] += e
    # for i in range(num_qubits):
    #     zero_freq_list = list()
    #     one_freq_list = list()
        

        

    for i in range(num_qubits):
        zero_freq = 0
        one_freq = 0
        for k, v in bin_phase_dict.items():
            if k[i] == '0':
                zero_freq += v
            elif k[i] == '1':
                one_freq += v
        qubit_list.append(abs(zero_freq - one_freq))
    normalized_list = [x/(pow(2, num_qubits-2) * 360) for x in qubit_list]
    normalized_list = [1 if x > 1 else x for x in normalized_list]
    normalized_list = [0 if math.isnan(x) else x for x in normalized_list]
    return normalized_list

def mag_analysis(num_qubits, mag_result):
    qubit_list = list()
    for i in range(num_qubits):
        zero_freq = 0
        one_freq = 0
        for k, v in mag_result.items():
            if k[i] == '0':
                zero_freq += v
            elif k[i] == '1':
                one_freq += v
        qubit_list.append(zero_freq - one_freq + 10000)
    # avg = sum(qubit_list) / len(qubit_list)
    # deviations = [abs(x - avg) for x in qubit_list]
    # normalized_deviation = [x / 10000 for x in deviations]
    normalized_deviation = [x / 20000 for x in qubit_list]
    return normalized_deviation

def entangle_analysis(content, num_qubits):
    all_states_num_minus = pow(2, num_qubits - 1)
    rate_of_dist = list()
    deviation_list = list()
    for lock_bit_idx in range(num_qubits):
        dist_0 = list()
        dist_1 = list()
        count_0 = 0
        count_1 = 0
        for k, e in content.items():
            if k[lock_bit_idx] == '0':
                dist_0.append(e)
                count_0 += e
            elif k[lock_bit_idx] == '1':
                dist_1.append(e)
                count_1 += e
        deviation = 0
        if count_0 == 0 or count_1 == 0:
            deviation_list.append(0)
        else:
            for i, d in enumerate(dist_0):
                deviation += abs(dist_0[i]/count_0 - dist_1[i]/count_1)
                deviation_list.append(deviation/2)

        # bin_dict_minus = gen_bin_dict(num_qubits - 1)
        # ob_bar_count = 0
        # for k, e in content.items():
        #     rest_bits = skip_bit(k, lock_bit_idx)
        #     bin_dict_minus[rest_bits] += e
        # for k, e in bin_dict_minus.items():
        #     if e > 0:
        #         ob_bar_count += 1
        # rate = np.around(ob_bar_count / all_states_num_minus, decimals = 3)
        # rate_of_dist.append(rate)
    # print(deviation_list)
    return deviation_list

def write_to_csv(mag_list, phase_list, entangle_list, mutator_name):
    with open(mutator_name + "_gen.csv", 'a+') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(mag_list)):
            writer.writerow([mag_list[i], phase_list[i], entangle_list[i]])

def main(num_qubits, mutator_name):
    circuit = Circuit(num_qubits)
    mutator = mutators[mutator_name]
    new_circuit = mutator.generate_circuit(circuit)
    vec_circuit = deepcopy(new_circuit)
    new_circuit.run_code()
    mag_result = new_circuit.results
    phase_result = vec_circuit.run_vec()
    entangle_result = entangle_analysis(new_circuit.results, num_qubits)
    # print(mag_result)
    # print(phase_result)
    mag_list = mag_analysis(num_qubits, mag_result)
    phase_list = phase_analysis(num_qubits, phase_result)
    write_to_csv(mag_list, phase_list, entangle_result, mutator_name)

if __name__ == "__main__":
    for i in range(100):
        num_qubits = 5
        for mutator in mutators.keys():
            main(num_qubits, mutator)