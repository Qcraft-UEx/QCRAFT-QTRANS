#!/usr/bin/env python
# coding: utf-8

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from numpy import pi
from qiskit.providers.basic_provider import BasicProvider
from qiskit_ibm_provider import IBMProvider
from qiskit.providers.jobstatus import JobStatus
import qiskit.qasm3


# def least_busy_backend_ibm(qb):
#     provider = IBMProvider('ibm-q', 'open', 'main')
#     backend = provider.backends(filters=lambda x: x.configuration().n_qubits >= qb and
#                                not x.configuration().simulator and x.status().operational==True)
#     backend = least_busy(backend)
#     return backend

# Ejecutar el circuito
def runIBM(machine, circuit, shots, token_IBM):
    
    if machine == "local":
        backend = BasicProvider().get_backend("basic_simulator")
        x=int(shots)
        transpiled_circuit = transpile(circuit, backend)
        job = backend.run(transpiled_circuit, shots=x)
        result = job.result()
        counts = result.get_counts()
        return counts
    else:

        gate_machines_arn = {
            'ibmq_qasm_simulator': 'ibmq_qasm_simulator',
            'simulator_statevector': 'simulator_statevector',
            'simulator_extended_stabilizer': 'simulator_extended_stabilizer',
            'simulator_stabilizer': 'simulator_stabilizer',
            'simulator_mps': 'simulator_mps',
            'ibm_kyoto': 'ibm_kyoto',
            'ibm_osaka': 'ibm_osaka',
            'ibm_brisbane': 'ibm_brisbane',
            'ibm_sherbrooke': 'ibm_sherbrooke'
        }    
        provider = IBMProvider(token=token_IBM)
        backend = provider.get_backend(gate_machines_arn[machine])
        x=int(shots)
        transpiled_circuit = transpile(circuit, backend)
        # keys for the device
        job = backend.run(transpiled_circuit, backend, shots=x)
        job_id = job.job_id()
        # result = job.result()
        # counts = result.get_counts()
        return job_id, None
    


def recover_task_resultIBM(job_id, token_IBM):
    print("Tarea cargada en executeCircuitIBM:", job_id)
    print("Token cargado en executeCircuitIBM:", token_IBM)
    provider = IBMProvider(token=token_IBM)
    
    try:
        # Obtener el trabajo asociado con el job_id
        job = provider.retrieve_job(job_id)
        if job is None:
            print("No se encontró ningún trabajo con el ID proporcionado.")
            return None
        
        status = job.status()
        print("Status of task:", status)
        if status == JobStatus.DONE:  # Comparamos con JobStatus.DONE en lugar de 'DONE'
            result = job.result()
            counts = result.get_counts()
            return counts
        elif status == JobStatus.CANCELLED:  # Comparamos con JobStatus.CANCELLED en lugar de 'CANCELLED'
            print("Task was cancelled.")
            return None
        else:
            print("Task is still running or has failed.")
            return None
    except Exception as e:
        print("Error al recuperar el trabajo:", e)
        return None