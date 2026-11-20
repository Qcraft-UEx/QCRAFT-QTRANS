import random
import string
import base64
import json
import os
import io
import re
import urllib.parse
from urllib.parse import unquote

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from rest_framework import viewsets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings

from .models import Link
from .serializers import LinkSerializer


def generate_unique_random_string(length=30):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    while Link.objects.filter(cadena=random_string).exists():
        random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def extraer_simbolos_de_url(url_quirk):
    """Extrae los símbolos de puertas custom (~...) que realmente aparecen colocados en los cables ('cols') de la URL de Quirk."""
    if not url_quirk or 'circuit=' not in url_quirk:
        return set()
    try:
        raw_fragment = url_quirk.split('circuit=', 1)[1].split('&', 1)[0]
        circ_json = json.loads(unquote(raw_fragment))
        simbolos = set()
        for col in circ_json.get('cols', []):
            for celda in col:
                if isinstance(celda, str) and celda.startswith('~'):
                    simbolos.add(celda.split(':', 1)[0])
        return simbolos
    except Exception:
        return set()


@csrf_exempt
def recibir_url_quirk(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url_quirk = data.get('urlQuirk')
        screenshot_data_url = data.get('screenshotUrl')
        gate_symbols = data.get('customGates', [])
        email = data.get('email', None)

        screenshot = None
        if screenshot_data_url:
            screenshot_data = screenshot_data_url.split(',')[1]
            screenshot_data_decoded = base64.b64decode(screenshot_data)
            screenshot = ContentFile(screenshot_data_decoded, name='screenshot.png')

        link = Link.objects.create(url=url_quirk, screenshot=screenshot)
        random_string = generate_unique_random_string()
        link.cadena = random_string
        link.save()

        simbolos_url = extraer_simbolos_de_url(url_quirk)
        todos_simbolos = set(gate_symbols or []) | simbolos_url
        if todos_simbolos:
            from circuitIdentity.models import CustomGate
            filtro = {'symbol__in': list(todos_simbolos)}
            if email:
                filtro['email'] = email
            for puerta in CustomGate.objects.filter(**filtro):
                puerta.links.add(link)

        return JsonResponse({'id': link.id, 'url': url_quirk, 'cadena': random_string}, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_url_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            url_quirk = data.get('urlQuirk', '')
            cadena_circuito = data.get('cadenaCircuito', '')
            screenshot_data_url = data.get('screenshotUrl', '')
            gate_symbols = data.get('customGates', [])
            email = data.get('email', None)

            link = Link.objects.get(cadena=cadena_circuito)

            if screenshot_data_url:
                if link.screenshot and os.path.isfile(os.path.join(settings.MEDIA_ROOT, link.screenshot.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, link.screenshot.name))

                screenshot_data = screenshot_data_url.split(',')[1]
                screenshot_data_decoded = base64.b64decode(screenshot_data)
                screenshot = ContentFile(screenshot_data_decoded, name='screenshot.png')
                link.screenshot = screenshot

            link.url = url_quirk
            link.save()

            from circuitIdentity.models import CustomGate
            link.custom_gates.clear()
            simbolos_url = extraer_simbolos_de_url(url_quirk)
            todos_simbolos = set(gate_symbols or []) | simbolos_url
            if todos_simbolos:
                filtro = {'symbol__in': list(todos_simbolos)}
                if email:
                    filtro['email'] = email
                for puerta in CustomGate.objects.filter(**filtro):
                    puerta.links.add(link)

            return JsonResponse({'url': link.url}, status=200)
        except Link.DoesNotExist:
            return JsonResponse({'error': 'No se encontró ninguna cadena de circuito asociada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error en el servidor'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def get_id_from_cadena(request):
    if request.method == 'GET':
        cadena = request.GET.get('cadena')
        try:
            link = Link.objects.get(cadena=cadena)
            return JsonResponse({'id': link.id}, status=200)
        except Link.DoesNotExist:
            return JsonResponse({'error': 'No se encontró ningún enlace asociado con la cadena proporcionada'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


def generar_diagrama_lenguaje(ecosystem, code):
    """Genera el diagrama visual (PNG en Base64 o ASCII) para cada lenguaje soportado."""
    try:
        if ecosystem == "qiskit":
            ns = {}
            exec(code, ns)
            qc = ns.get("circuit")
            if qc is not None:
                fig = qc.draw(output="mpl")
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return {"type": "image", "data": f"data:image/png;base64,{img_b64}"}

        elif ecosystem == "pennylane":
            import pennylane as qml
            ns = {}
            exec(code, ns)
            qnode = ns.get("circuit")
            dev = ns.get("device")
            if qnode is not None:
                try:
                    wires = list(dev.wires) if dev is not None else None
                    fig, _ = qml.draw_mpl(qnode, wire_order=wires)()
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                    plt.close(fig)
                    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    return {"type": "image", "data": f"data:image/png;base64,{img_b64}"}
                except Exception as mpl_err:
                    import traceback
                    print(f"[Aviso] draw_mpl falló en PennyLane: {mpl_err}")
                    traceback.print_exc()
                    ascii_diag = qml.draw(qnode, wire_order=wires)()
                    return {"type": "text", "data": str(ascii_diag)}

        elif ecosystem == "braket":
            ns = {}
            exec(code, ns)
            braket_qc = ns.get("circuit")
            if braket_qc is not None:
                return {"type": "text", "data": str(braket_qc.diagram())}

        elif ecosystem == "qasm2":
            from qiskit import QuantumCircuit
            qc = QuantumCircuit.from_qasm_str(code)
            fig = qc.draw(output="mpl")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
            plt.close(fig)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return {"type": "image", "data": f"data:image/png;base64,{img_b64}"}

        elif ecosystem == "qasm3":
            import qiskit.qasm3
            qasm3_clean = re.sub(r'\bqreg\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;', r'qubit[\2] \1;', code)
            qasm3_clean = re.sub(r'\bcreg\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;', r'bit[\2] \1;', qasm3_clean)
            qc = qiskit.qasm3.loads(qasm3_clean)
            fig = qc.draw(output="mpl")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
            plt.close(fig)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return {"type": "image", "data": f"data:image/png;base64,{img_b64}"}

    except Exception as e:
        print(f"[Aviso] No se pudo generar el diagrama para {ecosystem}: {e}")
    return None


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

            target = ['qiskit'] if ecosystem.startswith('qasm') else [ecosystem]
            qasm_ver = "2.0" if ecosystem == 'qasm2' else "3.0"

            result = run_pipeline(
                input_mode="algorithm",
                input_file=temp_file,
                target_providers=target,
                qasm_version=qasm_ver,
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
                    for file in os.listdir(qasm_dir):
                        if file.endswith(f"v{qasm_ver}.txt") or file.endswith(f"v{qasm_ver}.qasm"):
                            script_path = os.path.join(qasm_dir, file)
                            break
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
                diagram = generar_diagrama_lenguaje(ecosystem, translated_code)
                print("--- TRADUCCIÓN EXITOSA --- \n")
                return JsonResponse({'code': translated_code, 'diagram': diagram})

        except Exception as e:
            import traceback
            print("\n!!! ERROR DETALLADO EN LA TRADUCCIÓN !!!")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido, debe ser POST'}, status=405)


def expandir_custom_gates_en_url(url_quirk):
    """Despliega recursivamente las custom gates compuestas ('circuit') en una URL de Quirk."""
    if not url_quirk or '#circuit=' not in url_quirk:
        return url_quirk

    base, fragment = url_quirk.split('#circuit=', 1)
    circuit_data = json.loads(urllib.parse.unquote(fragment))
    gates_list = circuit_data.get('gates', [])
    gate_map = {g['id']: g for g in gates_list if 'id' in g}

    def expandir_cols(cols, depth=0):
        if depth > 10:
            return cols
        nuevas_cols = []
        for col in cols:
            controles = [(idx, val) for idx, val in enumerate(col) if val == '•']
            tiene_compuesta = any(
                str(token).split(':', 1)[0] in gate_map
                and 'circuit' in gate_map[str(token).split(':', 1)[0]]
                for token in col
            )

            if not tiene_compuesta:
                nuevas_cols.append(col)
                continue

            for idx, token in enumerate(col):
                if token in (1, '1', None, '•'):
                    continue
                gate_id = str(token).split(':', 1)[0]
                gate_def = gate_map.get(gate_id)

                if gate_def and 'circuit' in gate_def:
                    sub_cols = expandir_cols(gate_def['circuit'].get('cols', []), depth + 1)
                    for sub_col in sub_cols:
                        col_expandida = [1] * max(idx + len(sub_col), len(col))
                        for c_idx, c_val in controles:
                            col_expandida[c_idx] = c_val
                        for s_idx, s_val in enumerate(sub_col):
                            if s_val not in (1, '1', None):
                                col_expandida[idx + s_idx] = s_val
                        nuevas_cols.append(col_expandida)
                else:
                    col_simple = [1] * len(col)
                    for c_idx, c_val in controles:
                        col_simple[c_idx] = c_val
                    col_simple[idx] = token
                    nuevas_cols.append(col_simple)

        return nuevas_cols

    circuit_data['cols'] = expandir_cols(circuit_data.get('cols', []))
    circuit_data['gates'] = [g for g in gates_list if 'circuit' not in g]

    nuevo_fragment = urllib.parse.quote(json.dumps(circuit_data, separators=(',', ':')))
    return f"{base}#circuit={nuevo_fragment}"


@csrf_exempt
def verificar_equivalencia_zx(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url_quirk = data.get('url')
            qasm_code = data.get('qasm_code')

            if not url_quirk or not qasm_code:
                return JsonResponse({'error': 'Faltan parámetros (url o qasm_code)'}, status=400)

            from utils.zx_utils import quirk_to_zx_graph, qasm_to_zx_graph
            import pyzx as zx

            url_limpia = expandir_custom_gates_en_url(url_quirk)
            g1 = quirk_to_zx_graph(url_limpia)
            g2 = qasm_to_zx_graph(qasm_code)

            is_equivalent = zx.compare_tensors(g1, g2)

            return JsonResponse({'success': True, 'equivalent': is_equivalent}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)