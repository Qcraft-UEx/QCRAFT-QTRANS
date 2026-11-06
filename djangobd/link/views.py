import random
import string
from rest_framework import viewsets
from .models import Link
from .serializers import LinkSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import base64
import json
import os
from django.conf import settings

# Importamos qtrans para leer su ruta, y run_pipeline para ejecutar
import qtrans
from qtrans import run_pipeline

def generate_unique_random_string(length=30):
    """Genera una cadena aleatoria única de caracteres y números."""
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    # Verificar si la cadena generada ya existe en la base de datos
    while Link.objects.filter(cadena=random_string).exists():
        random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string

@csrf_exempt
def recibir_url_quirk(request):
    if request.method == 'POST':
        # Obtener los datos JSON del cuerpo de la solicitud
        data = json.loads(request.body)
        url_quirk = data.get('urlQuirk')
        screenshot_data_url = data.get('screenshotUrl')

        # Guardar la imagen en el servidor
        screenshot = None
        if screenshot_data_url:
            # Convertir la imagen en base64 a un archivo de imagen
            screenshot_data = screenshot_data_url.split(',')[1]  # Eliminar el encabezado 'data:image/png;base64,'
            screenshot_data_decoded = base64.b64decode(screenshot_data)
            screenshot = ContentFile(screenshot_data_decoded, name='screenshot.png')

        # Guardar la URL y la imagen en la base de datos
        link = Link.objects.create(url=url_quirk, screenshot=screenshot)
        
        # Generar cadena aleatoria única
        random_string = generate_unique_random_string()
        
        # Asociar la cadena aleatoria con el enlace
        link.cadena = random_string
        link.save()
        
        # Devolver la URL original, el ID generado y la cadena como respuesta con un código 200
        return JsonResponse({'id': link.id, 'url': url_quirk, 'cadena': random_string}, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_url_circuito(request):
    if request.method == 'POST':
        try:
            # Decodificar el cuerpo de la solicitud como JSON
            data = json.loads(request.body.decode('utf-8'))
            
            # Obtener los datos de la URL, la cadena del circuito y la nueva captura de pantalla
            url_quirk = data.get('urlQuirk', '')
            cadena_circuito = data.get('cadenaCircuito', '')
            screenshot_data_url = data.get('screenshotUrl', '')

            print("URL recibida:", url_quirk)
            print("Cadena de circuito recibida:", cadena_circuito)

            # Buscar si ya existe una entrada con la cadena de circuito
            link = Link.objects.get(cadena=cadena_circuito)

            # Guardar la nueva captura de pantalla si se proporciona
            if screenshot_data_url:
                # Eliminar la captura de pantalla antigua si existe
                if link.screenshot and os.path.isfile(os.path.join(settings.MEDIA_ROOT, link.screenshot.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, link.screenshot.name))

                # Convertir la nueva captura de pantalla de base64 a un archivo de imagen
                screenshot_data = screenshot_data_url.split(',')[1]
                screenshot_data_decoded = base64.b64decode(screenshot_data)
                screenshot = ContentFile(screenshot_data_decoded, name='screenshot.png')
                link.screenshot = screenshot

            # Actualizar la URL
            link.url = url_quirk
            link.save()

            # Devolver la URL actualizada como respuesta
            print("URL actualizada correctamente")
            return JsonResponse({'url': link.url}, status=200)
        except Link.DoesNotExist:
            print("Error: No se encontró ninguna cadena de circuito asociada")
            return JsonResponse({'error': 'No se encontró ninguna cadena de circuito asociada'}, status=404)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': 'Error en el servidor'}, status=500)
    else:
        print("Error: Método no permitido")
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def get_id_from_cadena(request):
    if request.method == 'GET':
        cadena = request.GET.get('cadena') # Obtener la cadena de los parámetros GET
        try:
            # Buscar el enlace asociado con la cadena
            link = Link.objects.get(cadena=cadena)
            return JsonResponse({'id': link.id}, status=200)
        except Link.DoesNotExist:
            return JsonResponse({'error': 'No se encontró ningún enlace asociado con la cadena proporcionada'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


# --- 2. NUEVA FUNCIÓN API PARA LA TRADUCCIÓN ---
# --- 2. NUEVA FUNCIÓN API PARA LA TRADUCCIÓN ---
# --- NUEVA FUNCIÓN API PARA LA TRADUCCIÓN MULTI-VERSIÓN ---
@csrf_exempt
def translate_circuit_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            ecosystem = data.get('ecosystem', 'qiskit') 
            
            print(f"\n--- INICIANDO TRADUCCIÓN A {ecosystem.upper()} ---")
            
            import qtrans
            from qtrans import run_pipeline
            qtrans_base_dir = os.path.dirname(os.path.abspath(qtrans.__file__))
            
            input_dir = os.path.join(qtrans_base_dir, "input")
            os.makedirs(input_dir, exist_ok=True)
            temp_file = "temp_api_circuit.json"
            temp_path = os.path.join(input_dir, temp_file)
            
            circuit_data = {
                "Circuito_API": {
                    "url": url,
                    "desc": "Traducción en vivo desde QCRAFT"
                }
            }
            
            with open(temp_path, "w") as f:
                json.dump(circuit_data, f)
            
            # Detectar ecosistema y versión QASM
            target = ['qiskit'] if ecosystem.startswith('qasm') else [ecosystem]
            qasm_ver = "2.0" if ecosystem == 'qasm2' else "3.0"

            result = run_pipeline(
                input_mode="algorithm",
                input_file=temp_file,
                target_providers=target,
                qasm_version=qasm_ver, # Pasamos la versión específica a QTransLIFIA
                capture_images=False,
                generate_qasm_images=False,
                generate_comparison=False,
                generate_zx=False,
                verbose=False
            )
            
            run_dir = result.get('run_dir')
            if not run_dir:
                raise Exception("Fallo interno: run_pipeline no devolvió un directorio de ejecución (run_dir)")
            
            script_path = None
            if ecosystem.startswith("qasm"):
                qasm_dir = os.path.join(run_dir, "algorithms_qasm")
                if os.path.exists(qasm_dir):
                    # 1º Intento: Buscar el archivo con el sufijo de versión exacto (_v2.0 o _v3.0)
                    for file in os.listdir(qasm_dir):
                        if file.endswith(f"v{qasm_ver}.txt") or file.endswith(f"v{qasm_ver}.qasm"):
                            script_path = os.path.join(qasm_dir, file)
                            break
                    # 2º Intento: Si no lo encuentra, coge el primer txt que haya
                    if not script_path:
                        for file in os.listdir(qasm_dir):
                            if file.endswith(".txt") or file.endswith(".qasm") or file.endswith(".json"):
                                script_path = os.path.join(qasm_dir, file)
                                break
            else:
                provider_folder = "ibm_qiskit" if ecosystem == "qiskit" else ("aws_braket" if ecosystem == "braket" else "xanadu_pennylane")
                script_path = os.path.join(run_dir, "migrated_circuits", provider_folder, "Circuito_API.py")
            
            if script_path and os.path.exists(script_path):
                with open(script_path, "r", encoding="utf-8") as f:
                    translated_code = f.read()
                print("--- TRADUCCIÓN EXITOSA --- \n")
                return JsonResponse({'code': translated_code})
            else:
                raise Exception(f"El traductor terminó, pero no se encontró el archivo generado en la carpeta.")
                
        except Exception as e:
            import traceback
            print("\n!!! ERROR DETALLADO EN LA TRADUCCIÓN !!!")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Método no permitido, debe ser POST'}, status=405)