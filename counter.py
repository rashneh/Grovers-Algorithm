from qiskit import *
from qiskit.circuit import *
import numpy as np
import math
from typing import List, Tuple

import grover


def qft(n: int) -> Gate:
    qc = QuantumCircuit(n)

    for i in reversed(range(n)):
        qc.h(i)
        for j in range(i):
            qc.cp(theta=math.pi / (2 ** (i - j)), control_qubit=i, target_qubit=j)
    
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)

    return qc.to_gate(label="QFT")


def quantum_counter(cnf: List[List[int]], num_vars: int, precision: int) -> Gate:
    num_qubits = grover.grover_iteration(cnf, num_vars).num_qubits

    precision_bits = QuantumRegister(precision, name='precision')
    qc = QuantumCircuit(precision_bits, QuantumRegister(num_qubits, name='grover_bits'))

    precision_indices = list(range(precision))
    grover_indices = list(range(precision, precision + num_qubits))

    qc.h(precision_bits)
    for i in precision_indices:
        grover_gate_iter = grover.grover(cnf, num_vars, 2 ** i)
        controlled_grover_gate_iter = grover_gate_iter.control()
        qc.append(controlled_grover_gate_iter, [i] + grover_indices)
    
    inverse_qft = qft(precision).inverse()
    qc.append(inverse_qft, precision_indices)

    print(qc)

    return qc.to_gate(label="Quantum Counter")