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
from mutator import RandomMutator, QFTMutator, UCNOTMutator
from copy import deepcopy
from oracle import FullAdder, Grover
import time
import termplotlib as tpl

CONFIG = {
    "circuit_path": "circuit.py", # test target circuit
    "budget": 1, # the budget of the number of test cases in one test suite
    "num_input_qubit": 1,
    "num_classical_bit": 1,
}

class Prometheus(object):
    def __init__(self, mutator, num_qubits):
        self.num_qubits = int(num_qubits)
        self.mutator = mutator
        self.circuit = Circuit(self.num_qubits)
        self.current_count = 0

    def testing(self):
        new_circuit = self.mutator.generate_circuit(self.circuit)
        logger.debug("Input circuit: ")
        print(new_circuit)
        copy_new_circuit = deepcopy(new_circuit)
        new_circuit.run_code()
        # oracle_circuit = FullAdder(copy_new_circuit, self.num_qubits)
        # test_circuit = Circuit(self.num_qubits)
        # for i in range(self.num_qubits):
        #     copy_new_circuit = test_circuit
        #     copy_new_circuit.code.h(i)
        oracle_circuit = Grover(copy_new_circuit, self.num_qubits)
        oracle_circuit.result_verify()

    def analyzer(self, all_outputs, latest_output):
        return "OK"

    def feedback(self, mutator, current_count):
        current_output = self.history_outputs[current_count]
        analyzed_output = self.analyzer(self.history_outputs, current_output)
        mutator.update_mutate_strategy(analyzed_output)
        pass

    def start_testing(self):
        budget = CONFIG['budget']
        while self.current_count < budget:
            if self.current_count % 10 == 0:
                logger.debug("Now on {} course".format(self.current_count))
                # logger.debug("Historical outputs {}".format(self.history_outputs))
            self.testing()
            self.current_count += 1
            time.sleep(1)

if __name__ == '__main__':
    num_qubits = 3
    mutator = RandomMutator()
    # mutator = QFTMutator()
    p = Prometheus(mutator, num_qubits)
    p.start_testing()