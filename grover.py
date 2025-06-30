from qiskit import *
from qiskit.circuit import *
from typing import List

import oracle

def diffuser(num_vars: int) -> Gate:
    if num_vars == 1:
        qc = QuantumCircuit(num_vars)
        qc.h(0)
        qc.x(0)
        qc.z(0)
        qc.x(0)
        qc.h(0)
        qc.z(0)
        qc.x(0)
        qc.z(0)
        qc.x(0)
    else:
        qc = QuantumCircuit(num_vars)
        qc.h(range(num_vars))
        qc.x(range(num_vars))
        qc.h(num_vars - 1)
        qc.mcx(list(range(num_vars-1)), num_vars-1)
        qc.h(num_vars - 1)
        qc.x(range(num_vars))
        qc.h(range(num_vars))
        qc.z(0)
        qc.x(0)
        qc.z(0)
        qc.x(0)
    
    return qc.to_gate(label="Diffuser")

def grover_iteration(cnf: List[List[int]], num_vars: int) -> Gate:
    pf_oracle = oracle.bf_to_phase_oracle(oracle.get_bitflip_oracle(cnf, num_vars), num_vars)
    diffuser_gate = diffuser(num_vars)
    qc = QuantumCircuit(pf_oracle.num_qubits)

    qc.append(pf_oracle, range(pf_oracle.num_qubits))
    qc.append(diffuser_gate, range(diffuser_gate.num_qubits))

    return qc.to_gate(label="Grover Iteration")

def grover(cnf: List[List[int]], num_vars: int, num_iters: int) -> Gate:
    one_grover_iteration_gate = grover_iteration(cnf, num_vars)
    qc = QuantumCircuit(one_grover_iteration_gate.num_qubits)

    qc.h(range(num_vars))
    for i in range(num_iters):
        qc.append(one_grover_iteration_gate, list(range(one_grover_iteration_gate.num_qubits)))
    
    return qc.to_gate(label=f"Grover {num_iters} Iterations")