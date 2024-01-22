import os
import sys
import math
from line import Circuit
from logzero import logger
from mutator import RandomMutator, QFTMutator, UCNOTMutator
import termplotlib as tpl

sample_num = 1000
d1 = {"00": 235, "01": 535, "10": 200, "11": 30}
d2 = {"00": 356, "01": 123, "10": 435, "11": 86}
d3 = {'1000': 128, '1100': 98, '1111': 2, '0001': 1676, '0000': 208, '0010': 1046, '0111': 1007, '0011': 919, '1011': 724, '0110': 428, '1101': 1625, '0101': 1144, '1110': 995}
d4 = {'1001': 2, '1000': 122, '1100': 114, '0001': 1583, '0110': 465, '1101': 1596, '0011': 925, '1011': 784, '0111': 956, '1110': 1009, '0101': 1156, '0000': 239, '0010': 1049}

def KSTest(d1, d2, sample_num):
    cum1, cum2 = 0, 0
    dic1_keys, dic2_keys = list(d1.keys()), list(d2.keys())
    new_d1, new_d2 = dict(), dict()
    for i in dic1_keys:
        cum1 += d1.get(i, 0)
        new_d1[i] = cum1
    for j in dic2_keys:
        cum2 += d2.get(j, 0)
        new_d2[j] = cum2
    keys = set(dic1_keys + dic2_keys)
    max_diver = 0
    for i in keys:
        a = abs(new_d1.get(i, 0) - new_d2.get(i, 0))
        if a > max_diver:
            max_diver = a
    return max_diver / sample_num

def CrossEntropy(d1, d2, sample_num):
    dic1_keys, dic2_keys = list(d1.keys()), list(d2.keys())
    keys = set(dic1_keys + dic2_keys)
    new_d1, new_d2 = dict(), dict()
    for i in dic1_keys:
        new_d1[i] = d1.get(i, 0) / sample_num
    for j in dic2_keys:
        new_d2[j] = d2.get(j, 0) / sample_num
    H = 0
    for k in keys:
        H -= new_d1.get(k, 0) * (math.log2(new_d2.get(k, 0)))
    return H

def KLDivergence(d1, d2, sample_num):
    dic1_keys, dic2_keys = list(d1.keys()), list(d2.keys())
    keys = set(dic1_keys + dic2_keys)
    new_d1, new_d2 = dict(), dict()
    for i in dic1_keys:
        new_d1[i] = (d1.get(i, 0) + 0.01) / sample_num
    for j in dic2_keys:
        new_d2[j] = (d2.get(j, 0) + 0.01) / sample_num
    H = 0
    for k in keys:
        H -= new_d1.get(k, 0) * (math.log2(new_d2.get(k, 0) / new_d1.get(k, 0)))
    return H

def JSDivergence(d1, d2, sample_num):
    dic1_keys, dic2_keys = list(d1.keys()), list(d2.keys())
    keys = set(dic1_keys + dic2_keys)
    M = {}
    for k in keys:
        M[k] = (d1.get(k, 0) + d2.get(k, 0)) / 2
    H = KLDivergence(d1, M, sample_num) + KLDivergence(d2, M, sample_num)
    return H/2

if __name__ == "__main__":
    mutator1 = UCNOTMutator()
    mutator2 = QFTMutator()
    mutator3 = RandomMutator()
    circuit = Circuit(4)
    c1 = mutator1.generate_circuit(circuit)
    print(c1)
    circuit = Circuit(4)
    c2 = mutator2.generate_circuit(circuit)
    circuit = Circuit(4)
    c3 = mutator3.generate_circuit(circuit)
    c1.run_code()
    c2.run_code()
    c3.run_code()
    result1 = c1.results
    bit_value, freq = list(result1.keys()), list(result1.values())
    figure = tpl.figure()
    figure.barh(freq, bit_value, show_vals = True)
    figure.show()
    print(c2)
    result2 = c2.results
    bit_value, freq = list(result2.keys()), list(result2.values())
    figure = tpl.figure()
    figure.barh(freq, bit_value, show_vals = True)
    figure.show()
    print(c3)
    # result3 = c3.results
    # bit_value, freq = list(result3.keys()), list(result3.values())
    # figure = tpl.figure()
    # figure.barh(freq, bit_value, show_vals = True)
    # figure.show()
    # logger.debug("KSTEST: {}".format(KSTest(result1, result2, 10000)))
    # logger.debug("CrossEntropy: {}".format(CrossEntropy(result1, result2, 10000)))
    # logger.debug("KLDivergense: {}".format(KLDivergence(result1, result2, 10000)))
    logger.debug("JSDivergence: {}".format(JSDivergence(d3, d4, 10000)))