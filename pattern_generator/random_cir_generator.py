import os
import os
import sys
from itertools import permutations as pm
import math
import numpy as np
import random
from pattern_generator.line import *
from copy import deepcopy
from pattern_generator.rotation import UU_CNOT_UU, UU_NOTC_UU, UU_Cal
from qiskit.circuit.library import QFT
import pattern_generator.mutator as mut


def cir_generator(template,num_qubit): #template是模版名 QFT或者CNOT   num_qubit：qubit数量
    if template == "QFT":
        circuit = Circuit(num_qubit)
        mutator = mut.QFTMutator()
        return mutator.generate_circuit(circuit).code    #return qc的代码，可以直接用qc进行接受并操作
    else:
        circuit = Circuit(num_qubit)
        mutator = mut.UCNOTMutator()
        return mutator.generate_circuit(circuit).code

if __name__ == "__main__":
    qc = cir_generator("QFT",5)
    print(type(qc))
    qc.cx(0,1)
    print(qc)