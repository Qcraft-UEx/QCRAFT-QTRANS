from django.shortcuts import render, get_object_or_404
from .models import CircuitIdentity, Results, ResultsDebug
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import ResultsDebugSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from deployment.models import Deployment
import json
from datetime import datetime
from executeCircuitIBM import runIBM, recover_task_resultIBM
from executeCircuitAWS import runAWS, recover_task_resultAWS


@csrf_exempt
def obtener_nombres_circuitos_por_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if email:
            circuitos = []
            circuit_identity_objects = CircuitIdentity.objects.filter(email=email)
            for circuit_identity in circuit_identity_objects:
                if ResultsDebug.objects.filter(result__id_circuito=circuit_identity.link_id).exists():
                    nombre_circuito = circuit_identity.nombre or f"ID: {circuit_identity.link_id}"
                    circuitos.append({
                        'id': circuit_identity.link_id,
                        'nombre': nombre_circuito,
                    })
            return JsonResponse({'circuitos': circuitos})
        return JsonResponse({'error': 'No se proporcionó el correo electrónico'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def obtener_resultados_circuito(request):
    if request.method == 'GET':
        circuito_id = request.GET.get('id')
        if circuito_id:
            resultados = ResultsDebug.objects.filter(
                result__id_circuito=circuito_id
            ).values(
                'id',
                'id_circuito_debug',
                'url_circuito_debug',
                'resultado_circuito_debug',
                'result__tipo_circuito',
                'result__tarea_id'
            )
            return JsonResponse({'resultados': list(resultados)})
        return JsonResponse({'error': 'No se proporcionó el ID del circuito'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def ejecutar_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            circuito_id = data.get('circuito_id')
            codigo_traducido = data.get('codigo_traducido')
            tipo_circuito = data.get('plataforma')
            maquina = data.get('maquina')
            shots = data.get('shots')
            email = data.get('email')

            if maquina != 'local':
                deployment_params = Deployment.objects.filter(email=email).first()
                if not deployment_params:
                    return JsonResponse({'success': False, 'circuito': "CREDENCIALES", 'tarea_id': None})
                private_key_aws = deployment_params.private_AWS
                public_key_aws = deployment_params.public_AWS
                s3_key_aws = deployment_params.s3_AWS
                token_IBM = deployment_params.token_IBM

            circuit_identity = get_object_or_404(CircuitIdentity, link_id=circuito_id)
            codigo_lines = codigo_traducido.split('\n')
            circuit_def = 'def circ():\n'
            if tipo_circuito == 'IBM':
                circuit_def += '\tfrom qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit\n'
                circuit_def += '\tfrom numpy import pi\n'
            for line in codigo_lines:
                if tipo_circuito == 'IBM' and 'from' not in line:
                    circuit_def += '\t' + line + '\n'
                elif tipo_circuito != 'IBM':
                    circuit_def += '\t' + line + '\n'
            circuit_def += 'circuit = circ()'
            loc = {}
            exec(circuit_def, globals(), loc)
            circuito = loc['circuit']
            if tipo_circuito == 'IBM':
                if maquina == 'local':
                    results_debug = runIBM(maquina, circuito, shots, '')
                    task_id = None
                else:
                    task_id, results_debug = runIBM(maquina, circuito, shots, token_IBM)
            elif tipo_circuito == 'AWS':
                if maquina == 'local':
                    results_debug = runAWS(maquina, circuito, shots, "", '', '', '')
                    task_id = None
                else:
                    task_id, results_debug = runAWS(maquina, circuito, shots, "", private_key_aws, public_key_aws, s3_key_aws)
            else:
                return JsonResponse({'success': False, 'circuito': "ERROR PLATAFORMA", 'tarea_id': None})

            result_obj = Results.objects.create(
                id_circuito=circuit_identity,
                codigo=None,
                tipo_circuito=tipo_circuito,
                timestamp=datetime.now(),
                tarea_id=task_id
            )

            ResultsDebug.objects.create(
                result=result_obj,
                id_circuito_debug=circuit_identity.link_id,
                url_circuito_debug=results_debug.get('url', '') if isinstance(results_debug, dict) else '',
                resultado_circuito_debug=results_debug.get('resultado', results_debug)
            )

            return JsonResponse({'success': True, 'circuito': results_debug, 'tarea_id': task_id})
        except Exception as e:
            print("Error al ejecutar circuito:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def check_task_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            email = data.get('email')
            tipo_circuito = data.get('tipo_circuito')

            deployment_params = Deployment.objects.filter(email=email).first()
            if tipo_circuito == 'IBM':
                task_load = recover_task_resultIBM(task_id, deployment_params.token_IBM)
            elif tipo_circuito == 'AWS':
                task_load = recover_task_resultAWS(task_id, deployment_params.private_AWS,
                                                  deployment_params.public_AWS, deployment_params.s3_AWS)
            else:
                return JsonResponse({'error': 'Plataforma desconocida'}, status=400)

            if task_load is not None:
                result_debug = ResultsDebug.objects.get(result__tarea_id=task_id)
                result_debug.resultado_circuito_debug = task_load
                result_debug.save()
                return JsonResponse({'result': task_load})
            return JsonResponse({'result': None})
        except Exception as e:
            print("Error en check_task_result:", e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def borrar_resultado(request, id_resultado):
    if request.method == 'DELETE':
        try:
            resultado = ResultsDebug.objects.get(pk=id_resultado)
            resultado.delete()
            return JsonResponse({'message': 'El resultado ha sido borrado correctamente'})
        except ResultsDebug.DoesNotExist:
            return JsonResponse({'error': 'El resultado no existe'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


class ResultsDebugViewSet(viewsets.ModelViewSet):
    queryset = ResultsDebug.objects.all()
    serializer_class = ResultsDebugSerializer

    def create(self, request, *args, **kwargs):
        id_circuito_debug = request.data.get('id_circuito_debug')
        print(f"ResultsDebugViewSet.create received: {request.data}")
        print(f"Buscando id_circuito_debug: {id_circuito_debug}")

        try:
            instance = ResultsDebug.objects.get(id_circuito_debug=id_circuito_debug)
            print(f"Instancia encontrada para actualización: {instance.pk}")

            instance.url_circuito_debug = request.data.get('url_circuito_debug', instance.url_circuito_debug)
            instance.resultado_circuito_debug = request.data.get('resultado_circuito_debug', instance.resultado_circuito_debug)
            instance.save()
            print("Instancia actualizada exitosamente.")
 
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ResultsDebug.DoesNotExist:
            print("Instancia no encontrada, creando nueva.")
            try:
                return super().create(request, *args, **kwargs)
            except Exception as e:
                print(f"Error al crear nueva instancia: {e}")
                raise e
        except Exception as e:
            print(f"Error inesperado en ResultsDebugViewSet.create: {e}")
            raise e


@csrf_exempt
def check_circuit_exists(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    id_circuito_debug = request.GET.get('id_circuito_debug')
    if not id_circuito_debug:
        return JsonResponse(
            {'error': 'No se proporcionó el id_circuito_debug'},
            status=400
        )

    result = ResultsDebug.objects.filter(
        id_circuito_debug=id_circuito_debug
    ).values('url_circuito_debug', 'resultado_circuito_debug').first()

    if result:
        return JsonResponse({
            'exists': True,
            'stored_url': result['url_circuito_debug'],
            'stored_result': result['resultado_circuito_debug']
        })

    return JsonResponse({'exists': False})
