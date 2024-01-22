import collections
import time
from enum import Enum
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Union, Set

import numpy as np
from z3 import Tactic, Or, And, If, Real, Bool

# 一些内置的操作门
from quantum_constraint_solver.symqv.constants import I_matrix, CNOT_matrix, SWAP_matrix

# 引入qbit的设定方法
from quantum_constraint_solver.symqv.expressions.qbit import QbitVal, Qbits
from quantum_constraint_solver.symqv.expressions.rqbit import RQbitVal, RQbits
from quantum_constraint_solver.symqv.expressions.complex import Complexes
from quantum_constraint_solver.symqv.globals import precision_format
from quantum_constraint_solver.symqv.models.gate import Gate
from quantum_constraint_solver.symqv.models.measurement import Measurement
from quantum_constraint_solver.symqv.models.state_sequence import StateSequence
from quantum_constraint_solver.symqv.operations.measurements import zero_measurement, one_measurement
from quantum_constraint_solver.symqv.solver import solve, write_smt_file, SpecificationType
from quantum_constraint_solver.symqv.utils_file.arithmetic import state_equals, state_equals_value, matrix_vector_multiplication, \
    complex_kron_n_ary, kron, state_equals_phase_oracle
from quantum_constraint_solver.symqv.utils_file.helpers import get_qbit_indices, identity_pad_gate, to_complex_matrix, \
    identity_pad_single_qbit_gates, are_qbits_reversed, are_qbits_adjacent, swap_transform_non_adjacent_gate

import subprocess


class Method(Enum):
    state_model = 'state_model'


class Circuit:
    def __init__(self, qbits: List[Union[QbitVal, RQbitVal]],
                 program: List[Union[Gate, List[Gate], Measurement]],
                 delta: float = 0.00001):

        self.qbits = qbits
        self.final_qbits = None
        self.num_qbits = len(self.qbits)
        self.program = program
        self.state = Complexes([f'psi_0_{i}' for i in range(2 ** self.num_qbits)])
        self.delta = delta
        self.initial_qbit_values = None
        self.initial_gate_applications = None
        self.initial_state_value = None
        self.specification = None
        self.specification_type = None
        self.is_equality_specification = None
        self.initialization_has_none_values = False
        # Tactic是z3中的一种策略或策略组合，用于构建和执行自动化的定理证明
        # “qfnra-nlsat”：用于处理非线性实数算术
        self.solver = Tactic('qfnra-nlsat').solver()

    def __str__(self):
        return ', '.join([str(gate) for gate in self.program])

    def initialize(self, values):
        """
        Initialize a quantum circuit with state values.
        :param values: list all states.
        :return: void.
        """
        basic_constraint = sum([elem.r ** 2 + elem.i ** 2 for elem in self.state]) == 1
        self.solver.add(basic_constraint)

        if self.initial_qbit_values is not None:
            print('Qbits are already initialized. Reinitializing.')

        for i, value in enumerate([v for v in values if v is not None]):
            self.solver.add(state_equals_value(self.state[i], value))

        self.initialization_has_none_values = any([value is None for value in values])
        self.initial_state_values = values

    def set_initial_gate_applications(self, gates: List[Gate]):
        # 直接用一组gate制备qubit的初始状态
        """
        Use gates to construct the initial state.
        :param gates:
        :return:
        """
        if self.initial_qbit_values is None:
            raise Exception("No initial values provided.")

        self.initial_gate_applications = gates

    def prove(self,
              dump_smt_encoding: bool = False,
              dump_solver_output: bool = False,
              measurement_branch: int = None,
              file_generation_only: bool = False,
              synthesize_repair: bool = False,
              overapproximation: bool = False) -> Union[
        Tuple[str, collections.OrderedDict, float], Tuple[NamedTemporaryFile, Set[str]]]:

        return self._prove_state_model(dump_smt_encoding,
                                       dump_solver_output,
                                       measurement_branch,
                                       file_generation_only,
                                       synthesize_repair,
                                       overapproximation)

    def _prove_state_model(self,
                           dump_smt_encoding: bool = False,
                           dump_solver_output: bool = False,
                           measurement_branch: int = None,
                           file_generation_only: bool = False,
                           synthesize_repair: bool = False,
                           overapproximation: bool = False) -> Union[Tuple[str, collections.OrderedDict, float],
    Tuple[NamedTemporaryFile, Set[str]]]:
        """
        Prove a quantum circuit according to the state model, symbolically encoding states as full vectors.
        :param dump_smt_encoding:  print the utils_file encoding.
        :param dump_solver_output: print the verbatim solver random_vector_output.
        :param measurement_branch: which measurement branch to consider (optional, only used by parallel evaluation).
        :param file_generation_only: only generate file, don't call solver.
        :param synthesize_repair: Synthesize repair to make the circuit fulfill the specification.
        :return: Solver random_vector_output.
        """
        start_full = time.time()

        state_sequence = StateSequence(self.qbits)

        if self.initial_gate_applications is not None:
            combined_initial_gate = identity_pad_gate(I_matrix, [0], self.num_qbits)

        for (i, operation) in enumerate(self.program):
            if isinstance(operation, Gate) or isinstance(operation, List):
                if len(state_sequence.measured_states) > 0:
                    raise Exception('Gates after measurement are not supported.')

                previous_state = state_sequence.states[-1]
                next_state = state_sequence.add_state()

                if isinstance(operation, Gate) and operation.oracle_value is None:
                    qbit_indices = get_qbit_indices([q.get_identifier() for q in self.qbits], operation.arguments)

                    if not are_qbits_adjacent(qbit_indices):
                        state_operation = swap_transform_non_adjacent_gate(operation.matrix,
                                                                           qbit_indices,
                                                                           self.num_qbits)
                    else:
                        state_operation = identity_pad_gate(operation.matrix
                                                            if not are_qbits_reversed(qbit_indices)
                                                            else operation.matrix_swapped,
                                                            qbit_indices,
                                                            self.num_qbits)

                    self.solver.add(state_equals(next_state,
                                                 matrix_vector_multiplication(to_complex_matrix(state_operation),
                                                                              previous_state)))
                elif isinstance(operation, Gate) and operation.oracle_value is not None:
                    self.solver.add(state_equals_phase_oracle(previous_state, next_state, operation.oracle_value))
                else:
                    state_operation = identity_pad_gate(I_matrix, [0], self.num_qbits)

                    for operation_element in operation:
                        qbit_indices = get_qbit_indices([q.get_identifier() for q in self.qbits],
                                                        operation_element.arguments)

                        if not are_qbits_adjacent(qbit_indices):
                            state_operation = swap_transform_non_adjacent_gate(operation_element.matrix,
                                                                               qbit_indices,
                                                                               self.num_qbits)
                        else:
                            state_operation = np.matmul(identity_pad_gate(operation_element.matrix
                                                                          if not are_qbits_reversed(qbit_indices)
                                                                          else operation_element.matrix_swapped,
                                                                          qbit_indices,
                                                                          self.num_qbits),
                                                        state_operation)

                    self.solver.add(state_equals(next_state,
                                                 matrix_vector_multiplication(to_complex_matrix(state_operation),
                                                                              previous_state)))
            elif isinstance(operation, Measurement):
                previous_state = state_sequence.states[-1]
                exists_measurement_state = len(state_sequence.measured_states) > 0

                if isinstance(operation.arguments, QbitVal):
                    measurement_states = state_sequence.add_measurement_state()

                    qbit_index = get_qbit_indices([q.get_identifier() for q in self.qbits], [operation.arguments])[0]

                    for (j, measurement_state) in enumerate(measurement_states):
                        measurement_operation = identity_pad_gate(zero_measurement
                                                                  if j % 2 == 0
                                                                  else one_measurement,
                                                                  [qbit_index],
                                                                  self.num_qbits)

                        if not exists_measurement_state:
                            self.solver.add(
                                state_equals(measurement_state,
                                             matrix_vector_multiplication(to_complex_matrix(measurement_operation),
                                                                          previous_state)))
                        else:
                            for state_before_element in previous_state:
                                self.solver.add(
                                    state_equals(measurement_state,
                                                 matrix_vector_multiplication(to_complex_matrix(measurement_operation),
                                                                              state_before_element)))
                else:
                    measurement_states = state_sequence.add_measurement_state(len(operation.arguments))

                    qbit_indices = get_qbit_indices([q.get_identifier() for q in self.qbits], operation.arguments)

                    num_digits = len('{0:b}'.format(len(measurement_states))) - 1
                    binary_format = '{0:0' + str(num_digits) + 'b}'

                    if measurement_branch is not None:
                        state_sequence.states[-1] = [measurement_states[measurement_branch]]
                        measurement_states = state_sequence.states[-1]

                    for (j, measurement_state) in enumerate(measurement_states):
                        bit_vector = binary_format.format(j if measurement_branch is None else measurement_branch)

                        measurement_ops = []

                        for b in bit_vector:
                            if b == '0':
                                measurement_ops.append(zero_measurement)
                            else:
                                measurement_ops.append(one_measurement)

                        combined_measurement = kron(measurement_ops)

                        measurement_operation = identity_pad_gate(combined_measurement,
                                                                  qbit_indices,
                                                                  self.num_qbits)

                        if not exists_measurement_state:
                            # First measured state
                            self.solver.add(
                                state_equals(measurement_state,
                                             matrix_vector_multiplication(to_complex_matrix(measurement_operation),
                                                                          previous_state)))
                        else:
                            # Existing measured states
                            raise Exception('No multi-measurement after other measurements.')
            else:
                raise Exception('Unsupported operation. Has to be either gate or measurement.')

        # 4.1 Repair synthesis:
        if self.final_qbits is not None and synthesize_repair is True:
            raise Exception('State model does not support repair')

        # 4.2 Final state qbits
        if self.final_qbits is not None:
            final_state_definition = complex_kron_n_ary([qbit.to_complex_list() for qbit in self.final_qbits])

            if len(state_sequence.measured_states) == 0:
                self.solver.add(state_equals(state_sequence.states[-1], final_state_definition))
            else:
                # build disjunction for the different measurement results
                disjunction_elements = []

                for final_state in state_sequence.states[-1]:
                    disjunction_elements.append(state_equals(final_state, final_state_definition))

                self.solver.add(Or(disjunction_elements))

        # 5 Call solver
        new_sexpr = self.solver.sexpr().replace("distinct", "=")
        print("circuit.py generate constraint.smt2!!!!!!!!!!!!")
        with open("test\\temp_file\constraint.smt2", "w+") as file:
            file.write(new_sexpr)
            file.write("\n(check-sat)")
            file.write("\n(get-model)")

        temp_file = NamedTemporaryFile(mode='w+b', suffix='.smt2', delete=False)

        with open(temp_file.name, "w") as text_file:
            text_file.write(new_sexpr)
            text_file.write("\n(check-sat)")
            text_file.write("\n(get-model)")

        qbit_identifiers = [qbit.get_identifier() for qbit in self.qbits]

        dreal_path = '/opt/dreal/4.21.06.2/bin/dreal'
        z3_path = '/usr/local/bin/z3'
        delta = 0.0001
        command = [dreal_path, '--precision', str(delta), temp_file.name] \
            if not isinstance(state_sequence.qbits[0], RQbitVal) else [z3_path, temp_file.name]

        result = subprocess.run(command, capture_output=True)

        end_full = time.time()
        time_full = end_full - start_full

        print(f'\nElapsed time {precision_format.format(time_full)} seconds.')
        return result, time_full


def _has_boolean_gates_only(program):
    for (i, gate) in enumerate(program):
        if gate.name not in ['I', 'X', 'SWAP', 'CNOT', 'CCX']:
            return False

    return True
