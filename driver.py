from qiskit import *
from qiskit.circuit import *
from qiskit.circuit.library.standard_gates import MCXGate
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qiskit.quantum_info import Statevector
import numpy as np

import sys

import math
import csv

import counter, grover, oracle

def read_csv_to_string_list(filename):
    rows = []
    with open(filename, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    return rows

def read_list_to_key(rows):
    key = {}
    next_num = 1
    for row in rows:
        for item in row:
            var = item.strip()
            if var == "":
                continue  # Skip empty strings
            # Remove a leading tilde if present.
            if var[0] == '~':
                var = var[1:].strip()
            if var not in key:
                key[var] = next_num
                next_num += 1
    return key

def convert_key_to_2dlist(key,rows):
    return_arr = []
    for row in rows:
        temp = []
        for name in row:
            if name == "":
                continue  # skip empty strings
            elif name[0] == '~':
                temp.append(key[name[1:].strip()]*-1)
            else:
                temp.append(key[name])
        return_arr.append(temp)
    
    return return_arr


def estimate_solution_count(cnf, num_vars, precision=5) -> int:
    qc_counter_gate = counter.quantum_counter(cnf, num_vars, precision)
    total_qubits = qc_counter_gate.num_qubits

    qc = QuantumCircuit(total_qubits, precision)
    qc.append(qc_counter_gate, list(range(total_qubits)))
    qc.measure(list(range(precision)), list(range(precision)))
    
    # Simulate the circuit using AerSimulator.
    sim = AerSimulator()
    compiled_circ = transpile(qc, sim)
    result = sim.run(compiled_circ, shots=1000).result()
    counts = result.get_counts(compiled_circ)
    
    total_shots = sum(counts.values())
    weighted_sum = 0
    for outcome, count in counts.items():
        # outcome is a binary string; convert it to an integer.
        x = int(outcome, 2)
        weighted_sum += x * count
    
    # Compute the estimated fraction from phase estimation.
    phi_est = weighted_sum / (total_shots * (2 ** precision))
    theta_est = math.pi * phi_est
    
    # Total search space size is N = 2^(num_vars)
    N = 2 ** num_vars
    M_est = N * (math.sin(theta_est)) ** 2

    # Return the estimated number of solutions, rounded to the nearest integer.
    return int(round(M_est))


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: ./%s [csv_file]" % sys.argv[0])
    
    csv_file = sys.argv[1]
    rows = read_csv_to_string_list(csv_file)
    key = read_list_to_key(rows)
    num_list = convert_key_to_2dlist(key,rows)

    print(f"COUNT - Counting solutions for {len(key)} variables...")
    M_est = estimate_solution_count(num_list, len(key), precision=5)
    
    print(f"COUNT - Estimated number of solutions: {M_est:.5f}")
    rounded_M = round(M_est)
    N = 2 ** len(key)

    if rounded_M == 0:
        optimal_iterations = (math.pi / 4) * math.sqrt(N / 1)
    else:
        optimal_iterations = (math.pi / 4) * math.sqrt(N / rounded_M)
    
    print(f"COUNT - Estimated number of Grover Iterations: {optimal_iterations}")    
    if rounded_M == 0:
        print("COUNT - No solutions expected, exiting")
        sys.exit(0)

    
    # If you still need to run your Driver, you can do so here.
    # For example:
    # driver = Driver(csv_file)
    # if driver.run_search():
    #     driver.print_solution()
    # else:
    #     print("GROVER: No solution found after %d attempts" % MAX_SEARCHES)

if __name__ == "__main__":
    main()
