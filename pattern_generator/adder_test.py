from qiskit import QuantumCircuit, execute, Aer, QuantumRegister, ClassicalRegister

def adder(mqc):
    q = QuantumRegister(4)
    c = ClassicalRegister(4)
    qc = QuantumCircuit(q, c)

    qc.ccx(1,2,3)
    qc.cx(1,2)
    qc.ccx(0,2,3)
    qc.cx(0,2)

    qc = mqc.compose(qc)
    for i in range(4):
        qc.measure(i, i)
    print(qc)

    backend = Aer.get_backend("aer_simulator")
    job = execute(qc, backend, shots = 10000).result().get_counts(qc)
    # counts = job.result().get_counts(qc)
    print(job)
    return job