import os
import sys
import termplotlib as tpl
from logzero import logger
from distance import KSTest, CrossEntropy

algos = [
    "adder",
    "bv",
    "dpc_pe",
    "dpc_qft",
    "grover",
    "pe",
    "qft",
    "rand_cliff"
]

def integrate(sign_vals, rest_vals):
    tmp_vals = dict()
    sign_keys = list(sign_vals.keys())
    for k in sign_vals.keys():
        if k not in tmp_vals.keys():
            tmp_vals[k] = 0
    for k, v in rest_vals.items():
        for kk in sign_keys:
            if k.endswith(kk) == True:
                tmp_vals[kk] += v
    return tmp_vals

def draw_bars(data):
    bit_value, freq = list(data.keys()), list(data.values())
    figure = tpl.figure()
    figure.barh(freq, bit_value, show_vals = True)
    figure.show()

def main(idx, mutator):
    folder_name = "exp-02-" + idx
    for algo in algos[1:2]:
        folder_path = os.path.join(folder_name, mutator)
        folder_file_list = os.listdir(folder_path)
        algo_file_list = [x for x in folder_file_list if algo in x]
        algo_file_list = sorted(algo_file_list)
        sign = algo_file_list[0]
        sign_vals = eval(open(os.path.join(folder_path, sign)).read())
        logger.debug("The dist of {0} by {1} mutator".format(algo, mutator))
        draw_bars(sign_vals)
        for rest in algo_file_list[1:]:
            rest_vals = eval(open(os.path.join(folder_path, rest)).read())
            logger.debug("The dist of integrated {0}".format(rest))
            draw_bars(integrate(sign_vals, rest_vals))
            # print(KSTest(sign_vals, rest_vals, 100000))

if __name__ == "__main__":
    main("03", "ucnot")
