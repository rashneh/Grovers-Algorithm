from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.circuit import Gate
from qiskit.circuit.library import MCXGate
from typing import List

def get_bitflip_oracle(cnf: List[List[int]], num_vars: int) -> Gate:
    inputs = QuantumRegister(num_vars, "inputs")
    output = QuantumRegister(1, "output")
    ancilla = AncillaRegister(len(cnf), "ancilla")
    qc = QuantumCircuit(inputs, output, ancilla, name="BitFlipOracle")
    # ancilla (indices num_vars+1 to num_vars+len(cnf)).

    for i, clause in enumerate(cnf):
        ancilla_index = num_vars + 1 + i # initialize ancilla to |1>
        qc.x(qc.qubits[ancilla_index])

        set = [abs(literal) - 1 for literal in clause]
        ctrl_state_int = 0
        for bit_idx, literal in enumerate(clause):
            if literal < 0:
                ctrl_state_int |= (1 << bit_idx)
        clause_mcx = MCXGate(len(set), ctrl_state=ctrl_state_int)
        set_qubits = [qc.qubits[idx] for idx in set]
        target_qubit = qc.qubits[ancilla_index]
        qc.append(clause_mcx, set_qubits + [target_qubit])
    
    # ccx all ancilla qubits to flip output qubit
    if len(cnf) > 0:
        final_ctrl_state = (1 << len(cnf)) - 1  # all ancilla must be |1>
        final_mcx = MCXGate(len(cnf), ctrl_state=final_ctrl_state)
        ancilla_qubits = qc.qubits[num_vars+1 : num_vars+1+len(cnf)]
        output_qubit = qc.qubits[num_vars]
        qc.append(final_mcx, list(ancilla_qubits) + [output_qubit])
    
    # reset qubits
    for i in reversed(range(len(cnf))):
        clause = cnf[i]
        controls = [abs(literal) - 1 for literal in clause]
        ctrl_state_int = 0
        for bit_idx, literal in enumerate(clause):
            if literal < 0:
                ctrl_state_int |= (1 << bit_idx)
        clause_mcx = MCXGate(len(controls), ctrl_state=ctrl_state_int)
        control_qubits = [qc.qubits[idx] for idx in controls]
        target_qubit = qc.qubits[num_vars + i + 1]
        qc.append(clause_mcx, control_qubits + [target_qubit])
        qc.x(qc.qubits[num_vars + i + 1])
    
    return qc.to_gate(label="BitFlipOracle")


def bf_to_phase_oracle(bf_oracle: Gate, num_vars: int) -> Gate:
    n_qubits = bf_oracle.num_qubits
    output_bit = num_vars  #output qubit is at index num_vars
    qc = QuantumCircuit(n_qubits, name="PhaseOracle")
    qc.x(output_bit)
    qc.h(output_bit)
    qc.append(bf_oracle, range(n_qubits))
    qc.h(output_bit)
    qc.x(output_bit)
    return qc.to_gate(label="PhaseOracle")