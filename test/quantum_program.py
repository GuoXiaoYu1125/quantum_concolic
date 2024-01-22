from qiskit import QuantumCircuit, Aer, transpile


def check_state_eq(qc, target_probability, delta):
    state_len = len(target_probability)
    qubits_num = int(pow(state_len, 0.5))
    qubits_state = [bin(i)[2:].zfill(qubits_num) for i in range(state_len)]
    qc.measure_all()
    simulator = Aer.get_backend('aer_simulator')
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=10000).result().get_counts()
    target = True
    for i in range(state_len):
        if (job.get(qubits_state[i], 0) / 10000) < target_probability[i] - delta or (
                job.get(qubits_state[i], 0) / 10000) > target_probability[i] + delta:
            target = False
    return target


def quantum_program(x, qc):
    # quantum circuit generation
    a = 0
    print(qc.state)
    qc.h(0)
    qc.z(0)
    if x > 50:
        qc.h(1)
        qc.cx(0, 1)
        a += 1

    # classical control
    if check_state_eq(qc, [0.25, 0.2, 0.2, 0.35], 0.01):
        return a
    else:
        return a + 2


def expected_result():
    return [0, 1, 2, 3]
