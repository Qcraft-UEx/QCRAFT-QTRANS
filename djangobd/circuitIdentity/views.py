# import json
# import random
# import requests
# import os
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.middleware.csrf import get_token
# from django.core.exceptions import ObjectDoesNotExist
# from django.conf import settings
# from urllib.parse import urljoin
# from rest_framework import viewsets

# from .models import CircuitIdentity, CustomGate
# from link.models import Link
# from .serializers import CircuitIdentitySerializer

# @csrf_exempt
# def guardar_info(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             link_id = data.get('link_id')
#         except json.JSONDecodeError:
#             email = request.POST.get('email')
#             link_id = request.POST.get('link_id')

#         if not email or not link_id:
#             return JsonResponse({'success': False, 'error': 'Email o link_id faltante'}, status=400)

#         try:
#             link = Link.objects.get(id=link_id)
#         except Link.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'El link no existe'}, status=404)

#         try:
#             circuito = CircuitIdentity.objects.create(email=email)
#             circuito.link_id.set([link])
#             print('Datos guardados correctamente:', email, link_id)
#             return JsonResponse({'success': True})
#         except Exception as e:
#             print('Error al guardar información:', e)
#             return JsonResponse({'success': False, 'error': 'Error al guardar información'}, status=500)
#     else:
#         return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# @csrf_exempt
# def obtener_url_y_nombre_por_email(request):
#     if request.method == 'GET':
#         email = request.GET.get('email')
#         if not email:
#             return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)
        
#         try:
#             circuit_identities = CircuitIdentity.objects.filter(email=email)
#             circuitos = []
#             for circuit_identity in circuit_identities:
#                 for link in circuit_identity.link_id.all():
#                     nombre = circuit_identity.nombre if circuit_identity.nombre else f'Circuito {link.id}'
#                     screenshot_url = link.screenshot.url if link.screenshot else None
#                     if screenshot_url:
#                         screenshot_url = urljoin('http://127.0.0.1:8000/' + settings.MEDIA_URL, screenshot_url)

#                     puertas = link.custom_gates.all()
#                     custom_gates_data = [{
#                         'id': p.gate_id,
#                         'name': p.name,
#                         'symbol': p.symbol,
#                         'definition': p.definition
#                     } for p in puertas]

#                     circuitos.append({
#                         'id': link.id,
#                         'url': link.url,
#                         'nombre': nombre,
#                         'cadena': link.cadena,
#                         'url_desplegada': circuit_identity.url_desplegada,
#                         'screenshot_url': screenshot_url,
#                         'custom_gates': custom_gates_data
#                     })

#             if not circuitos:
#                 return JsonResponse({'error': 'No se encontraron circuitos asociados al correo electrónico proporcionado'}, status=404)
            
#             return JsonResponse({'circuitos': circuitos})
        
#         except Exception as e:
#             print('Error al obtener los circuitos:', e)
#             return JsonResponse({'error': 'Error al obtener los circuitos'}, status=500)
#     else:
#         return JsonResponse({'error': 'Método no permitido'}, status=405)

# @csrf_exempt
# def actualizar_nombre_circuito(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             link_id = data.get('link_id') 
#             nuevo_nombre = data.get('nuevo_nombre')
            
#             CircuitIdentity.objects.filter(link_id=link_id).update(nombre=nuevo_nombre)
#             return JsonResponse({'success': True, 'link_id': link_id})
#         except Exception as e:
#             print("Error al actualizar el nombre del circuito:", e)
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Método no permitido'}, status=405)

# @csrf_exempt
# def lanzar_servicio(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             url = data.get('url')
#             id_circuito = data.get('id')
            
#             post_data = {"new_url": url}
#             headers = {'Content-Type': 'application/json'}
#             response = requests.post('http://quantumservicesdeployment.spilab.es:8084/new_circuit', json=post_data, headers=headers)

#             if response.status_code == 200:
#                 service_url = response.json().get('path')
#                 try:
#                     circuito = CircuitIdentity.objects.get(link_id=id_circuito)
#                     circuito.url_desplegada = service_url
#                     circuito.save()
#                     return JsonResponse({'success': True, 'service_url': service_url})
#                 except CircuitIdentity.DoesNotExist:
#                     return JsonResponse({'success': False, 'error': 'El circuito no existe'}, status=404)
#             else:
#                 return JsonResponse({'success': False, 'error': 'Error al obtener la URL del servicio'}, status=500)
#         except Exception as e:
#             print("Error al lanzar el servicio:", e)
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Método no permitido'}, status=405)

# @csrf_exempt
# def borrar_circuito(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             link_id = data.get('link_id') 

#             if not email or not link_id:
#                 return JsonResponse({'success': False, 'error 0': 'Email y link_id son requeridos'}, status=400)

#             link = Link.objects.get(id=link_id)
#             circuito = CircuitIdentity.objects.filter(email=email, link_id=link).first()

#             if circuito is None:
#                 return JsonResponse({'success': False, 'error 1': 'Circuito no encontrado para este usuario'}, status=404)

#             circuito.link_id.remove(link)
#             if circuito.link_id.count() == 0:
#                 circuito.delete()

#             return JsonResponse({'success': True, 'message': 'El circuito fue eliminado correctamente'})

#         except Link.DoesNotExist:
#             return JsonResponse({'success': False, 'error 2': 'Link no encontrado'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error 3': str(e)}, status=500)
#     else:
#         return JsonResponse({'error 4': 'Método no permitido'}, status=405)

# def get_csrf_token(request):
#     csrf_token = get_token(request)
#     return JsonResponse({'csrfToken': csrf_token})

# @csrf_exempt
# def guardar_puerta_custom(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             name = data.get('name')
#             symbol = data.get('symbol')
#             definition = data.get('definition')
#             link_id = data.get('link_id', None)

#             if not email or not symbol or not definition:
#                 return JsonResponse({'success': False, 'error': 'Campos faltantes (email, symbol, definition)'}, status=400)

#             name = name or symbol
#             gate_id = f"cg_{symbol}_{random.randint(1000, 9999)}"

#             puerta, created = CustomGate.objects.update_or_create(
#                 email=email,
#                 name=name,
#                 defaults={
#                     'gate_id': gate_id,
#                     'symbol': symbol,
#                     'definition': definition
#                 }
#             )
            
#             if link_id:
#                 try:
#                     link = Link.objects.get(id=link_id)
#                     puerta.links.add(link)
#                 except Link.DoesNotExist:
#                     pass

#             return JsonResponse({'success': True, 'gate_id': puerta.gate_id}, status=201 if created else 200)
#         except Exception as e:
#             print("Error al guardar puerta custom:", e)
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Método no permitido'}, status=405)

# @csrf_exempt
# def obtener_puertas_custom(request):
#     if request.method == 'GET':
#         email = request.GET.get('email')
#         if not email:
#             return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)

#         try:
#             puertas = CustomGate.objects.filter(email=email)
#             data = [
#                 {
#                     'id': p.gate_id,
#                     'name': p.name,
#                     'symbol': p.symbol,
#                     'definition': p.definition
#                 }
#                 for p in puertas
#             ]
#             return JsonResponse({'custom_gates': data}, status=200)
#         except Exception as e:
#             print("Error al obtener puertas custom:", e)
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Método no permitido'}, status=405)

# class CircuitIdentityViewSet(viewsets.ModelViewSet):
#     queryset = CircuitIdentity.objects.all()
#     serializer_class = CircuitIdentitySerializer





import json
import math
import random
import requests
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from urllib.parse import urljoin
from rest_framework import viewsets

from .models import CircuitIdentity, CustomGate
from link.models import Link
from .serializers import CircuitIdentitySerializer

from urllib.parse import urljoin, unquote


def normalizar_definicion_matriz(raw_def):
    if raw_def is None:
        return ""
    if not isinstance(raw_def, str):
        raw_def = json.dumps(raw_def)
    def_str = raw_def.strip().strip('"').strip()
    if def_str.startswith("{{") and def_str.endswith("}}") and "},{" not in def_str and "}, {" not in def_str:
        inner = def_str[2:-2]
        elems = [e.strip() for e in inner.split(",") if e.strip()]
        dim = round(math.sqrt(len(elems)))
        if dim * dim == len(elems) and dim > 1:
            filas = [", ".join(elems[r * dim:(r + 1) * dim]) for r in range(dim)]
            return "{{" + "}, {".join(filas) + "}}"
    return def_str


@csrf_exempt
def guardar_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            link_id = data.get('link_id')
        except json.JSONDecodeError:
            email = request.POST.get('email')
            link_id = request.POST.get('link_id')

        if not email or not link_id:
            return JsonResponse({'success': False, 'error': 'Email o link_id faltante'}, status=400)

        try:
            link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El link no existe'}, status=404)

        try:
            circuito = CircuitIdentity.objects.create(email=email)
            circuito.link_id.set([link])
            print('Datos guardados correctamente:', email, link_id)
            return JsonResponse({'success': True})
        except Exception as e:
            print('Error al guardar información:', e)
            return JsonResponse({'success': False, 'error': 'Error al guardar información'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
def obtener_url_y_nombre_por_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)
        
        try:
            circuit_identities = CircuitIdentity.objects.filter(email=email)
            circuitos = []
            for circuit_identity in circuit_identities:
                for link in circuit_identity.link_id.all():
                    nombre = circuit_identity.nombre if circuit_identity.nombre else f'Circuito {link.id}'
                    screenshot_url = link.screenshot.url if link.screenshot else None
                    if screenshot_url:
                        screenshot_url = urljoin('http://127.0.0.1:8000/' + settings.MEDIA_URL, screenshot_url)

                    puertas = link.custom_gates.all()
                    custom_gates_data = [{
                        'id': p.gate_id,
                        'name': p.name,
                        'symbol': p.symbol,
                        'definition': normalizar_definicion_matriz(p.definition)
                    } for p in puertas]

                    circuitos.append({
                        'id': link.id,
                        'url': link.url,
                        'nombre': nombre,
                        'cadena': link.cadena,
                        'url_desplegada': circuit_identity.url_desplegada,
                        'screenshot_url': screenshot_url,
                        'custom_gates': custom_gates_data
                    })

            if not circuitos:
                return JsonResponse({'error': 'No se encontraron circuitos asociados al correo electrónico proporcionado'}, status=404)
            
            return JsonResponse({'circuitos': circuitos})
        
        except Exception as e:
            print('Error al obtener los circuitos:', e)
            return JsonResponse({'error': 'Error al obtener los circuitos'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_nombre_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            link_id = data.get('link_id') 
            nuevo_nombre = data.get('nuevo_nombre')
            
            CircuitIdentity.objects.filter(link_id=link_id).update(nombre=nuevo_nombre)
            return JsonResponse({'success': True, 'link_id': link_id})
        except Exception as e:
            print("Error al actualizar el nombre del circuito:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def lanzar_servicio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            id_circuito = data.get('id')
            
            post_data = {"new_url": url}
            headers = {'Content-Type': 'application/json'}
            response = requests.post('http://quantumservicesdeployment.spilab.es:8084/new_circuit', json=post_data, headers=headers)

            if response.status_code == 200:
                service_url = response.json().get('path')
                try:
                    circuito = CircuitIdentity.objects.get(link_id=id_circuito)
                    circuito.url_desplegada = service_url
                    circuito.save()
                    return JsonResponse({'success': True, 'service_url': service_url})
                except CircuitIdentity.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'El circuito no existe'}, status=404)
            else:
                return JsonResponse({'success': False, 'error': 'Error al obtener la URL del servicio'}, status=500)
        except Exception as e:
            print("Error al lanzar el servicio:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


# @csrf_exempt
# def borrar_circuito(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             link_id = data.get('link_id') 

#             if not email or not link_id:
#                 return JsonResponse({'success': False, 'error 0': 'Email y link_id son requeridos'}, status=400)

#             link = Link.objects.get(id=link_id)
#             circuito = CircuitIdentity.objects.filter(email=email, link_id=link).first()

#             if circuito is None:
#                 return JsonResponse({'success': False, 'error 1': 'Circuito no encontrado para este usuario'}, status=404)

#             circuito.link_id.remove(link)
#             if circuito.link_id.count() == 0:
#                 circuito.delete()

#             return JsonResponse({'success': True, 'message': 'El circuito fue eliminado correctamente'})

#         except Link.DoesNotExist:
#             return JsonResponse({'success': False, 'error 2': 'Link no encontrado'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error 3': str(e)}, status=500)
#     else:
#         return JsonResponse({'error 4': 'Método no permitido'}, status=405)


@csrf_exempt
def borrar_circuito(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body) if request.body else {}
            email = data.get('email') or request.GET.get('email')
            link_id = data.get('link_id') or request.GET.get('link_id')

            if not email or not link_id:
                return JsonResponse({'success': False, 'error 0': 'Email y link_id son requeridos'}, status=400)

            link = Link.objects.get(id=link_id)
            circuito = CircuitIdentity.objects.filter(email=email, link_id=link).first()

            if circuito is None:
                return JsonResponse({'success': False, 'error 1': 'Circuito no encontrado para este usuario'}, status=404)

            circuito.link_id.remove(link)
            if circuito.link_id.count() == 0:
                circuito.delete()

            return JsonResponse({'success': True, 'message': 'El circuito fue eliminado correctamente'})

        except Link.DoesNotExist:
            return JsonResponse({'success': False, 'error 2': 'Link no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error 3': str(e)}, status=500)
    else:
        return JsonResponse({'error 4': 'Método no permitido'}, status=405)


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


# @csrf_exempt
# def guardar_puerta_custom(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             name = data.get('name')
#             symbol = data.get('symbol')
#             definition = normalizar_definicion_matriz(data.get('definition'))
#             link_id = data.get('link_id', None)
#             overwrite = data.get('overwrite', False)

#             if not email or not symbol or not definition:
#                 return JsonResponse({'success': False, 'error': 'Campos faltantes (email, symbol, definition)'}, status=400)

#             name = (name or symbol).strip()

#             # Comprobar si ESTE usuario ya tiene otra puerta con el mismo nombre
#             puerta_existente = CustomGate.objects.filter(email=email, name__iexact=name).first()
#             if puerta_existente and not overwrite:
#                 return JsonResponse({
#                     'success': False,
#                     'error': f'Ya tienes una puerta llamada "{name}". Elige otro nombre distinto.'
#                 }, status=409)

#             if puerta_existente:
#                 puerta_existente.symbol = symbol
#                 puerta_existente.definition = definition
#                 puerta_existente.save()
#                 puerta = puerta_existente
#                 created = False
#             else:
#                 gate_id = f"cg_{symbol}_{random.randint(1000, 9999)}"
#                 puerta = CustomGate.objects.create(
#                     email=email,
#                     gate_id=gate_id,
#                     name=name,
#                     symbol=symbol,
#                     definition=definition
#                 )
#                 created = True

#             if link_id:
#                 try:
#                     link = Link.objects.get(id=link_id)
#                     puerta.links.add(link)
#                 except Link.DoesNotExist:
#                     pass

#             return JsonResponse({'success': True, 'gate_id': puerta.gate_id}, status=201 if created else 200)
#         except Exception as e:
#             print("Error al guardar puerta custom:", e)
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
def guardar_puerta_custom(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name')
            symbol = data.get('symbol')
            # Guardar la definición tal cual llega, solo limpiando espacios laterales
            raw_def = data.get('definition')
            definition = raw_def.strip() if isinstance(raw_def, str) else str(raw_def or '').strip()
            link_id = data.get('link_id', None)
            overwrite = data.get('overwrite', False)

            if not email or not symbol or not definition:
                return JsonResponse({'success': False, 'error': 'Campos faltantes (email, symbol, definition)'}, status=400)

            name = (name or symbol).strip()

            puerta_existente = CustomGate.objects.filter(email=email, name__iexact=name).first()
            if puerta_existente and not overwrite:
                return JsonResponse({
                    'success': False,
                    'error': f'Ya tienes una puerta llamada "{name}". Elige otro nombre distinto.'
                }, status=409)

            if puerta_existente:
                puerta_existente.symbol = symbol
                puerta_existente.definition = definition
                puerta_existente.save()
                puerta = puerta_existente
                created = False
            else:
                gate_id = f"cg_{symbol}_{random.randint(1000, 9999)}"
                puerta = CustomGate.objects.create(
                    email=email,
                    gate_id=gate_id,
                    name=name,
                    symbol=symbol,
                    definition=definition
                )
                created = True

            if link_id:
                try:
                    link = Link.objects.get(id=link_id)
                    puerta.links.add(link)
                except Link.DoesNotExist:
                    pass

            return JsonResponse({'success': True, 'gate_id': puerta.gate_id}, status=201 if created else 200)
        except Exception as e:
            print("Error al guardar puerta custom:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)




import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generar_diagrama_puerta(puerta, todas_las_puertas):
    """Dibuja el subcircuito de una puerta personalizada o su matriz unitaria en Base64."""
    raw_def = normalizar_definicion_matriz(puerta.definition)

    # Caso 1: Puerta definida por matriz (ej: {{1, 0}, {0, -1}})
    if raw_def.startswith("{{"):
        filas_txt = raw_def.strip("{}").split("}, {")
        matriz_formateada = "\n".join(f"[ {f} ]" for f in filas_txt)
        return {"type": "matrix", "data": matriz_formateada}

    # Caso 2: Puerta compuesta por subcircuito JSON (ej: {"cols": [["H"], ["X"]]})
    try:
        circ_json = json.loads(raw_def)
        cols = circ_json.get("cols", [])
        if not cols:
            return None

        # Mapa de puertas compuestas del usuario por si hay puertas anidadas (ej: ~mihz -> ~prueba)
        gate_map = {}
        for p in todas_las_puertas:
            p_def = normalizar_definicion_matriz(p.definition)
            if p_def.startswith("{") and not p_def.startswith("{{"):
                try:
                    gate_map[p.symbol] = json.loads(p_def)
                except Exception:
                    pass

        def expandir(c_list, depth=0):
            if depth > 6:
                return c_list
            res = []
            for col in c_list:
                tiene_sub = any(str(t).split(":")[0] in gate_map for t in col if t not in (1, "1", None, "•"))
                if not tiene_sub:
                    res.append(col)
                    continue
                for idx, tok in enumerate(col):
                    if tok in (1, "1", None, "•"):
                        continue
                    gid = str(tok).split(":")[0]
                    if gid in gate_map:
                        for sub_c in expandir(gate_map[gid].get("cols", []), depth + 1):
                            nueva = [1] * max(len(col), idx + len(sub_c))
                            for c_i, c_v in enumerate(col):
                                if c_v == "•":
                                    nueva[c_i] = "•"
                            for s_i, s_v in enumerate(sub_c):
                                if s_v not in (1, "1", None):
                                    nueva[idx + s_i] = s_v
                            res.append(nueva)
                    else:
                        nueva = [1] * len(col)
                        nueva[idx] = tok
                        res.append(nueva)
            return res

        cols_exp = expandir(cols)
        n_wires = max((len(c) for c in cols_exp), default=1)
        n_cols = len(cols_exp)

        fig_w = max(3.2, n_cols * 1.1 + 1.0)
        fig_h = max(1.4, n_wires * 0.8 + 0.4)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_xlim(-0.5, n_cols + 0.3)
        ax.set_ylim(-0.6, n_wires - 0.4)
        ax.invert_yaxis()
        ax.axis("off")

        # Dibujar cables horizontales y etiquetas q0, q1...
        for w in range(n_wires):
            ax.plot([0, n_cols], [w, w], color="#333333", linewidth=1.5, zorder=1)
            ax.text(-0.15, w, f"q{w}", va="center", ha="right", fontsize=10, fontweight="bold", color="#333")

        # Dibujar puertas y controles en cada columna
        for c_idx, col in enumerate(cols_exp):
            x = c_idx + 0.5
            activos = [i for i, v in enumerate(col) if v not in (1, "1", None)]
            if len(activos) > 1:
                ax.plot([x, x], [min(activos), max(activos)], color="#1a73e8", linewidth=1.8, zorder=2)

            for w_idx, tok in enumerate(col):
                if tok in (1, "1", None):
                    continue
                if tok == "•":
                    ax.scatter([x], [w_idx], color="#1a73e8", s=60, zorder=4)
                else:
                    label = str(tok).lstrip("~")
                    rect = patches.FancyBboxPatch(
                        (x - 0.28, w_idx - 0.25), 0.56, 0.5,
                        boxstyle="round,pad=0.04",
                        facecolor="#e8f0fe", edgecolor="#1a73e8", linewidth=1.6, zorder=3
                    )
                    ax.add_patch(rect)
                    ax.text(x, w_idx, label, va="center", ha="center", fontsize=10, fontweight="bold", color="#174ea6", zorder=5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"type": "image", "data": f"data:image/png;base64,{img_b64}"}
    except Exception as e:
        print(f"[Aviso] No se pudo dibujar la puerta {puerta.name}: {e}")
        return None


@csrf_exempt
def obtener_puertas_custom(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)

        try:
            puertas = list(CustomGate.objects.filter(email=email).order_by('id'))
            data = [
                {
                    'id': p.gate_id,
                    'name': p.name,
                    'symbol': p.symbol,
                    'definition': normalizar_definicion_matriz(p.definition),
                    'diagram': generar_diagrama_puerta(p, puertas)
                }
                for p in puertas
            ]
            return JsonResponse({'custom_gates': data}, status=200)
        except Exception as e:
            print("Error al obtener puertas custom:", e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)





@csrf_exempt
def editar_puerta_custom(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            gate_id = data.get('gate_id')
            nuevo_nombre = data.get('name')
            nuevo_simbolo = data.get('symbol')
            nueva_definicion = data.get('definition')

            if not email or not gate_id:
                return JsonResponse({'success': False, 'error': 'Faltan email o gate_id'}, status=400)

            puerta = CustomGate.objects.filter(email=email, gate_id=gate_id).first()
            if not puerta:
                return JsonResponse({'success': False, 'error': 'Puerta no encontrada'}, status=404)

            if nuevo_nombre:
                nombre_limpio = nuevo_nombre.strip()
                # Verificar que el mismo usuario no tenga OTRA puerta con ese mismo nombre
                duplicada = CustomGate.objects.filter(email=email, name__iexact=nombre_limpio).exclude(id=puerta.id).exists()
                if duplicada:
                    return JsonResponse({
                        'success': False,
                        'error': f'Ya tienes otra puerta llamada "{nombre_limpio}". No puedes tener dos puertas con el mismo nombre.'
                    }, status=409)
                puerta.name = nombre_limpio

            if nuevo_simbolo:
                puerta.symbol = nuevo_simbolo.strip()
            if nueva_definicion is not None and str(nueva_definicion).strip() != "":
                puerta.definition = normalizar_definicion_matriz(nueva_definicion)

            puerta.save()
            return JsonResponse({'success': True, 'gate_id': puerta.gate_id})
        except Exception as e:
            print("Error al editar puerta custom:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def borrar_puerta_custom(request):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido, debe ser DELETE'}, status=405)

    try:
        email = request.GET.get('email')
        gate_id = request.GET.get('gate_id')

        if not email or not gate_id:
            return JsonResponse({'success': False, 'error': 'Faltan email o gate_id'}, status=400)

        puerta = CustomGate.objects.filter(email=email, gate_id=gate_id).first()
        if not puerta:
            return JsonResponse({'success': False, 'error': 'Puerta no encontrada'}, status=404)

        circuitos_en_uso = set()

        # Obtener todos los links del usuario a través de CircuitIdentity
        links_usuario = []
        for ci in CircuitIdentity.objects.filter(email=email).prefetch_related('link_id'):
            links_usuario.extend(ci.link_id.all())

        ids_usuario = {l.id for l in links_usuario}

        # 1. Revisar relación directa ManyToMany (puerta.links) filtrada por los circuitos del usuario
        for link in puerta.links.filter(id__in=ids_usuario):
            circuitos_en_uso.add(link.id)

        # 2. Revisar el contenido real de la URL de Quirk por si la tabla intermedia estaba vacía
        for link in links_usuario:
            if link.id in circuitos_en_uso:
                continue
            if link.url and 'circuit=' in link.url:
                try:
                    raw_fragment = link.url.split('circuit=', 1)[1].split('&', 1)[0]
                    circ_json = json.loads(unquote(raw_fragment))

                    cols_str = json.dumps(circ_json.get('cols', []))
                    if (
                        f'"{puerta.symbol}"' in cols_str
                        or f'"{puerta.symbol}:' in cols_str
                        or (puerta.name and (f'"{puerta.name}"' in cols_str or f'"{puerta.name}:' in cols_str))
                    ):
                        circuitos_en_uso.add(link.id)
                except Exception:
                    pass

        if circuitos_en_uso:
            ids_ordenados = sorted(circuitos_en_uso)
            ids_texto = ", ".join(str(cid) for cid in ids_ordenados)
            etiqueta = "el circuito con id" if len(ids_ordenados) == 1 else "los circuitos con id"
            return JsonResponse({
                'success': False,
                'in_use': True,
                'circuit_ids': ids_ordenados,
                'error': f'No se puede borrar esta puerta porque se está usando en {etiqueta}: {ids_texto}'
            }, status=409)

        puerta.delete()
        return JsonResponse({'success': True, 'message': 'Puerta eliminada correctamente'}, status=200)

    except Exception as e:
        print("Error al borrar puerta custom:", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


class CircuitIdentityViewSet(viewsets.ModelViewSet):
    queryset = CircuitIdentity.objects.all()
    serializer_class = CircuitIdentitySerializer



