import ast

from quantum_constraint_solver.symqv.expressions.qbit import Qbits
from quantum_constraint_solver.symqv.models.circuit import Circuit
from quantum_constraint_solver.qiskit_plugin import operations_to_program
from quantum_constraint_solver.symqv.expressions.complex import Complexes

def eq_constraint(prob_constraint, symbolic_state_list, circuit):
    for index, prob in enumerate(prob_constraint):
        target_state = symbolic_state_list[index]
        circuit.solver.add(target_state.r ** 2 + target_state.i ** 2 == prob)
    return circuit

def neq_constraint(prob_constraint, symbolic_state_list, circuit):
    for index, prob in enumerate(prob_constraint):
        target_state = symbolic_state_list[index]
        circuit.solver.add(target_state.r ** 2 + target_state.i ** 2 != prob)
    return circuit

def quantum_constraint_solver(num_qbits, operations, prob_constraint, flag):
    qbit_name = [f"q{i}" for i in range(num_qbits)]
    symbolic_qubit_list = Qbits(qbit_name)
    num_operations = len(operations)

    # generate symbolic circuit
    circuit = Circuit(symbolic_qubit_list, program=operations_to_program(num_qbits, operations))

    circuit.initialize([None for i in range(num_qbits)])
    final_state_list = [f"psi_{num_operations}_{i}" for i in range(2 ** num_qbits)]
    initial_state_list = [f"psi_{0}_{i}" for i in range(2 ** num_qbits)]

    symbolic_state_list = Complexes(final_state_list)

    if flag == "==":
        circuit = eq_constraint(prob_constraint, symbolic_state_list, circuit)
    elif flag == "!=":
        circuit = neq_constraint(prob_constraint, symbolic_state_list, circuit)

    result, time_full = circuit.prove(overapproximation=False)

    # print(result)
    output = result.stdout.decode("utf-8")
    quantum_result = output.replace("define-fun", "").replace("() Real", "!").split("\n")[2:-2]

    result_dict = {}
    for obj in quantum_result:
        state_name, state_value = obj.split("!")
        state_name, state_value = state_name[4:], ast.literal_eval(state_value[1:-1])
        if state_name[4] == "0":
            result_dict[state_name] = state_value

    result_state = []
    for state_obj in initial_state_list:
        temp1, temp2 = result_dict.get(state_obj + ".r "), result_dict.get(state_obj + ".i ")
        if type(temp1).__name__ == "list":
            temp1 = temp1[0]
        if type(temp2).__name__ == "list":
            temp2 = temp2[0]
        result_state.append(complex(temp1, temp2))

    return result_state, time_full


if __name__ == "__main__":
    result, time = quantum_constraint_solver(2, ["h(0)", "z(0)", "h(1)", "cnot(0,1)"], [0.25, 0.2, 0.2, 0.35], flag="==")
    print(result)