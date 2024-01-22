import os
import sys
from logzero import logger
# from mutator import Mutator
from line import Circuit, H_Gate
from qiskit import (
    #IBMQ,
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    execute,
    Aer,
)
from mutator import RandomMutator, QFTMutator, UCNOTMutator, UCNOTMutator2, AllHadmard
from oracle import Grover
from copy import deepcopy
from sat import Generator
import time
import random
import termplotlib as tpl

mutators = {
    "random": RandomMutator(),
    "qft": QFTMutator(),
    "ucnot": UCNOTMutator(),
    "u2": UCNOTMutator2(),
    "Hs": AllHadmard()
}

RUN_BUDGET = 100
generator = Generator(4)
instance = generator.constant_instance()

def main(mutator_name, num_qubits, save_dir, inst_path):
    for run in range(RUN_BUDGET):
        circuit = Circuit(num_qubits)
        mutator = mutators[mutator_name]
        new_circuit = mutator.generate_circuit(circuit)
        grover = Grover(new_circuit, num_qubits, instance, load_inst_from_file=inst_path) # 4 clause
        verified = grover.result_verify()
        save_path = os.path.join(save_dir, mutator_name + '.random_vector_output')
        with open(save_path, 'a+') as f:
            if len(f.readlines()) >= 100:
                logger.debug("The answer of {} is enough".format(mutator_name))
                break
            if verified == True:
                print("Answer {} is verified.".format(grover.result_of_grover), file = f)
            else:
                print("Answer {} is incorrect.".format(grover.result_of_grover), file = f)

if __name__ == "__main__":
    num_qubits = 3
    names = list(mutators.keys())
    prefix = 'exp-03-'
    available_oracles = ['03', '05', '07', '12', '13', '16', '24', '26']
    for i in range(20):
        logger.debug("Now in {} run".format(str(i).zfill(2)))
        oracle = random.choice(available_oracles)
        save_dir = prefix + str(i).zfill(2)
        if os.path.exists(save_dir) == False:
            os.mkdir(save_dir)
        file_list = os.listdir(save_dir)
        for mutator in mutators.keys():
            file_path = os.path.join(save_dir, mutator+'.random_vector_output')
            main(mutator, num_qubits, save_dir, 'inst/' + oracle + '.or')