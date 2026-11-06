from django.shortcuts import render
from .models import CircuitIdentity, Results
from rest_framework import viewsets
from .serializers import ResultsSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
from deployment.models import Deployment
from threading import Thread
import json
from datetime import datetime
from executeCircuitIBM import runIBM
from executeCircuitIBM import recover_task_resultIBM
from executeCircuitAWS import runAWS
from executeCircuitAWS import recover_task_resultAWS


@csrf_exempt
def obtener_nombres_circuitos_por_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if email:
            circuitos = []
            circuit_identity_objects = CircuitIdentity.objects.filter(email=email)
            
            for circuit_identity in circuit_identity_objects:
                if Results.objects.filter(id_circuito=circuit_identity).exists():
                    
                    # 1. Obtenemos el primer enlace asociado para extraer su ID correctamente
                    primer_link = circuit_identity.link_id.first()
                    # 2. Por seguridad, si no tiene enlace, usamos el ID de la identidad
                    numero_circuito = primer_link.id if primer_link else circuit_identity.id
                    
                    # 3. Generamos el nombre
                    nombre_circuito = circuit_identity.nombre if circuit_identity.nombre else f"Circuito {numero_circuito}"
                    
                    circuitos.append({
                        'id': circuit_identity.id, 
                        'nombre': nombre_circuito,
                    })
            return JsonResponse({'circuitos': circuitos})
        else:
            return JsonResponse({'error': 'No se proporcionó el correo electrónico'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def obtener_resultados_circuito(request):
    if request.method == 'GET':
        circuito_id = request.GET.get('id')
        if circuito_id:
            resultados = Results.objects.filter(id_circuito=circuito_id).values('id', 'id_circuito', 'codigo', 'tipo_circuito', 'timestamp', 'tarea_id')
            return JsonResponse({'resultados': list(resultados)})
        else:
            return JsonResponse({'error': 'No se proporcionó el ID del circuito'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def ejecutar_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)
            circuito_id = data.get('circuito_id')
            codigo_traducido = data.get('codigo_traducido')
            tipo_circuito = data.get('plataforma')
            maquina = data.get('maquina')
            shots = data.get('shots')
            email = data.get('email')

            if maquina != 'local':
                deployment_params = Deployment.objects.filter(email=email).first()
                if deployment_params is None:
                    results = "CREDENCIALES"
                    return JsonResponse({'success': False, 'circuito': results, 'tarea_id': None})
                private_key_aws = deployment_params.private_AWS
                public_key_aws = deployment_params.public_AWS
                s3_key_aws = deployment_params.s3_AWS
                token_IBM = deployment_params.token_IBM

            if codigo_traducido:
                circuit_identity = get_object_or_404(CircuitIdentity, link_id=circuito_id)

                # --- LÓGICA PARA IBM Y AWS (Ejecución de código Python) ---
                if tipo_circuito in ['IBM', 'AWS']:
                    codigo_traducido_lineas = codigo_traducido.split('\n')
                    codigo_script = 'def circ():\n'
                    if tipo_circuito == 'IBM':
                        codigo_script += '\tfrom qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit\n'
                        codigo_script += '\tfrom qiskit.circuit.library import YGate, ZGate\n'
                        codigo_script += '\tfrom numpy import pi\n'
                    
                    for line in codigo_traducido_lineas:
                        if tipo_circuito == 'IBM':
                            if 'from' not in line:
                                codigo_script += '\t' + line + '\n'
                        else:
                            codigo_script += '\t' + line + '\n'
                            
                    # AQUÍ ESTÁ LA CLAVE: Retornar el circuito para que no devuelva None
                    codigo_script += '\treturn circuit\n'
                    codigo_script += 'circuito_creado = circ()'

                    loc = {}
                    try:
                        exec(codigo_script, globals(), loc)
                        circuito = loc['circuito_creado']
                    except Exception as e:
                        import traceback
                        print("------ ERROR EN EL EXEC DE PYTHON ------")
                        traceback.print_exc()
                        return JsonResponse({'success': False, 'circuito': 'ERROR', 'tarea_id': None})
                    
                    if tipo_circuito == 'IBM':
                        try:
                            if maquina == 'local':
                                token_IBM = ''
                                results = runIBM(maquina, circuito, shots, token_IBM)
                            else:
                                task_id, results = runIBM(maquina, circuito, shots, token_IBM)
                        except Exception as e:
                            import traceback
                            print("------ ERROR AL EJECUTAR IBM ------")
                            traceback.print_exc()
                            results = "ERROR"
                            task_id = "ERROR"
                            return JsonResponse({'success': False, 'circuito': results, 'tarea_id': None})
                            
                    if tipo_circuito == 'AWS':
                        try:
                            if maquina == 'local':
                                private_key_aws = ''
                                public_key_aws = ''
                                s3_key_aws = ''
                                results = runAWS(maquina, circuito, shots, "", private_key_aws, public_key_aws, s3_key_aws)
                            else:
                                task_id, results = runAWS(maquina, circuito, shots, "", private_key_aws, public_key_aws, s3_key_aws)
                        except Exception as e:
                            import traceback
                            print("------ ERROR AL EJECUTAR AWS ------")
                            traceback.print_exc()
                            results = "ERROR"
                            task_id = "ERROR"
                            return JsonResponse({'success': False, 'circuito': results, 'tarea_id': None})
                            
                # --- NUEVA LÓGICA PARA OPENQASM 2 Y 3 (Simulación en local con Qiskit) ---
                elif tipo_circuito in ['QASM2', 'QASM3']:
                    try:
                        from qiskit_aer import AerSimulator
                        
                        if tipo_circuito == 'QASM2':
                            from qiskit import QuantumCircuit
                            circuito_qiskit = QuantumCircuit.from_qasm_str(codigo_traducido)
                        else:
                            from qiskit import qasm3
                            circuito_qiskit = qasm3.loads(codigo_traducido)
                            
                        if 'measure' not in codigo_traducido.lower():
                            circuito_qiskit.measure_all()
                            
                        simulador = AerSimulator()
                        job = simulador.run(circuito_qiskit, shots=int(shots))
                        conteos = job.result().get_counts()
                        results = json.dumps(conteos)
                        task_id = None
                        
                    except Exception as e:
                        import traceback
                        print("------ ERROR EN QASM ------")
                        traceback.print_exc()
                        return JsonResponse({'success': False, 'circuito': 'ERROR', 'tarea_id': None})

                print("Circuito ejecutado exitosamente:", results)
            
                Results.objects.create(
                    id_circuito=circuit_identity,
                    codigo=results,
                    tipo_circuito=tipo_circuito,
                    timestamp=datetime.now(),
                    tarea_id=task_id if (tipo_circuito in ['AWS', 'IBM']) and maquina != 'local' else None
                )

                return JsonResponse({'success': True, 'circuito': results, 'tarea_id': task_id if (tipo_circuito in ['AWS', 'IBM']) and maquina != 'local' else None})
            else:
                return JsonResponse({'success': False, 'error': 'No se proporcionó ningún código traducido'}, status=400)
        except Exception as e:
            print("Error general durante la ejecución:", e)
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def check_task_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            email = data.get('email')
            tipo_circuito = data.get('tipo_circuito')
            print("ID de la tarea:", task_id)

            deployment_params = Deployment.objects.filter(email=email).first()
            print("Private key of AWS:", deployment_params.private_AWS)
            print("Public key of AWS:", deployment_params.public_AWS)
            print("S3 key of AWS:", deployment_params.s3_AWS)
            print("Token of IBM:", deployment_params.token_IBM)
            print("Tipo de circuito:", tipo_circuito)


            if tipo_circuito == 'IBM':
                token_IBM = deployment_params.token_IBM
                print("Token de IBM:", token_IBM)
                task_load = recover_task_resultIBM(task_id, token_IBM)
            if tipo_circuito == 'AWS':
                private_key_aws = deployment_params.private_AWS
                public_key_aws = deployment_params.public_AWS
                s3_key_aws = deployment_params.s3_AWS
                task_load = recover_task_resultAWS(task_id, private_key_aws, public_key_aws, s3_key_aws)


            print("Resultado de la tarea:", task_load)
            if task_load is not None:
                # Convierte task_load a una cadena de texto JSON
                task_load_json = json.dumps(task_load)
                result = Results.objects.get(tarea_id=task_id)
                result.codigo = task_load_json
                result.save()
                return JsonResponse({'result': task_load_json})
            else:
                return JsonResponse({'result': None})

        except Exception as e:
            print("Error durante la verificación de la tarea:", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    

@csrf_exempt
def borrar_resultado(request, id_resultado):
    if request.method == 'DELETE':
        try:
            resultado = Results.objects.get(pk=id_resultado)
            resultado.delete()
            return JsonResponse({'message': 'El resultado ha sido borrado correctamente'})
        except Results.DoesNotExist:
            return JsonResponse({'error': 'El resultado no existe'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


class ResultsViewSet(viewsets.ModelViewSet):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer