import os
import sys
from line import Circuit
from mutator import RandomMutator, UCNOTMutator, QFTMutator
from logzero import logger

RUN_TIME = 10
# SAVE_DIR = "exp-01-09"
# if os.path.exists(SAVE_DIR) == False:
#     os.mkdir(SAVE_DIR)
NUM_QUBITS = 8
mutators = [RandomMutator, UCNOTMutator, QFTMutator]

def main(num_qubits):
    for run_idx in range(RUN_TIME):
        logger.debug(run_idx)
        save_dir = 'exp-01-' + str(num_qubits).zfill(2)
        if os.path.exists(save_dir) == False:
            os.mkdir(save_dir)
        exp_path = os.path.join(save_dir, "run_" + str(run_idx).zfill(2))
        if os.path.exists(exp_path) == False:
            os.mkdir(exp_path)
        for m in mutators:
            # load mutator
            mutator = m()
            mutator_name = mutator.__class__.__name__
            logger.debug(mutator_name)
            circuit = Circuit(num_qubits)
            new_circuit = mutator.generate_circuit(circuit)
            # new_circuit.run_code()
            target_path = os.path.join(exp_path, mutator_name)
            if os.path.exists(target_path) == False:
                os.mkdir(target_path)
            hanlder1 = open(os.path.join(target_path, 'circuit'), 'w')
            print(new_circuit.code.qasm(), file = hanlder1)
            # hanlder2 = open(os.path.join(target_path, 'results'), 'w')
            # results = new_circuit.results
            # print(results, file = hanlder2)

if __name__ == "__main__":
    for i in range(4, NUM_QUBITS):
        main(i)