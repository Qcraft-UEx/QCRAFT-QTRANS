from braket.circuits import Circuit, Gate, Observable
from braket.circuits import circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice
import numpy as np
from fractions import Fraction
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice
from braket.aws import AwsQuantumTask
import boto3
import os
import time


def runAWS(machine, circuit, shots, s3_folder, private_key_aws, public_key_aws, s3_key_aws):
    x = int(shots)

    print("Machine:", machine)

    if machine=="local":
        device = LocalSimulator()
        result = device.run(circuit, shots=x).result()
        counts = dict(result.measurement_counts)
        print(counts)
        return counts

        
        
    machines={'sv1':'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            'tn1':'arn:aws:braket:::device/quantum-simulator/amazon/tn1',
            'dm1':'arn:aws:braket:::device/quantum-simulator/amazon/dm1',
            'ionq':'arn:aws:braket:us-east-1::device/qpu/ionq/Harmony',
            'ionq Aria 1' : 'arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1',
            'ionq Aria 2' : 'arn:aws:braket:us-east-1::device/qpu/ionq/Aria-2',
            'ionq Forte' : 'arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1',
            'rigetti' : 'arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3',
            'oqc lucy' : 'arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy',
            'quera aquila' : 'arn:aws:braket:us-east-1::device/qpu/quera/Aquila',
            'garnet' : 'arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet'
            }    
    
    if machine not in machines:
        raise ValueError("Unknown machine name")

    # Establecer la región correcta para el dispositivo
    regions = {
        'sv1': 'us-west-2',  
        'tn1': 'us-west-2',  
        'ionq': 'us-east-1',
        'ionq Aria 1': 'us-east-1',
        'ionq Aria 2': 'us-east-1',
        'ionq Forte': 'us-east-1',
        'rigetti': 'us-west-1',
        'oqc lucy': 'eu-west-2',
        'quera aquila': 'us-east-1',
        'garnet': 'eu-north-1'
    }

    region = regions[machine]
    print("Region:", region)
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region

    os.environ["AWS_ACCESS_KEY_ID"] = public_key_aws
    os.environ["AWS_SECRET_ACCESS_KEY"] = private_key_aws

    device = AwsDevice(machines[machine])
    print("Device:", device)

    if "sv1" not in machine and "tn1" not in machine:
        # Keys for the device
        print("NOT SV1")
        task = device.run(circuit, s3_folder, shots=x, poll_timeout_seconds=5 * 24 * 60 * 60) # Hacer lo mismo que con ibm para recuperar los resultados, guardar el id, usuarios... y despues en el scheduler, al iniciarlo, buscar el el bucket s3 si están los resultados, si no, esperar a que lleguen
        task_id = task.id
        # METER A DICCIONARIO LO DE ABAJO ANTES DE EJECUTAR
        # counts = recover_task_result(task).measurement_counts
        return task_id, None
    else:
        print("SV1")
        task = device.run(circuit, s3_folder, shots=x)
        task_id = task.id
        counts = dict(task.result().measurement_counts)
        return task_id, counts
    

def recover_task_resultAWS(task_load, private_key_aws, public_key_aws, s3_key_aws):
    os.environ["AWS_ACCESS_KEY_ID"] = public_key_aws
    os.environ["AWS_SECRET_ACCESS_KEY"] = private_key_aws
    print("Task load:", task_load)
    # recover task
    task = AwsQuantumTask(arn=task_load)
    status = task.state()
    print('Status of (reconstructed) task:', status)
    print('\n')
    # wait for job to complete
    # terminal_states = ['COMPLETED', 'FAILED', 'CANCELLED']
    if status == 'COMPLETED':
        # get results
        return dict(task.result().measurement_counts)
        # return dict(task_load.result().measurement_counts)
    print("Se devolverá None")
    return None


