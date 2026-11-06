from django.shortcuts import render
from .models import CircuitIdentity, Link
from rest_framework import viewsets
from .serializers import CircuitIdentitySerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
import json
import requests
import os
from django.conf import settings
from urllib.parse import urljoin


        

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
            # Obtener el objeto Link correspondiente al ID
            link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El link no existe'}, status=404)

        try:
            # Crear el objeto CircuitIdentity sin el link todavía
            circuito = CircuitIdentity.objects.create(email=email)

            # Establecer la relación ManyToMany después
            circuito.link_id.set([link])  # O puedes usar link_id si ya lo tienes como objeto

            print('Datos guardados correctamente:', email, link_id)
            return JsonResponse({'success': True})
        except Exception as e:
            print('Error al guardar información:', e)
            return JsonResponse({'success': False, 'error': 'Error al guardar información'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


"""
@csrf_exempt
def guardar_info(request):
    if request.method == 'POST':
        # Intenta obtener datos del cuerpo de la solicitud JSON
        try:
            data = json.loads(request.body)
            email = data.get('email')
            link_id = data.get('link_id')
        except json.JSONDecodeError:
            # Si no se puede analizar como JSON, intenta obtenerlos como datos de formulario
            email = request.POST.get('email')
            link_id = request.POST.get('link_id')

        if not email or not link_id:
            return JsonResponse({'success': False, 'error': 'Email o link_id faltante'}, status=400)

        try:


            # Verificar si ya existe una entrada con el mismo link_id
            existing_entry = CircuitIdentity.objects.get(link_id=link_id)
            return JsonResponse({'success': False, 'error': 'El link_id ya está registrado'}, status=400)
        except ObjectDoesNotExist:
            # Si no existe, crear una nueva entrada
            try:
                CircuitIdentity.objects.create(email=email, link_id=link_id)
                print('Datos guardados correctamente:', email, link_id)
                return JsonResponse({'success': True})
            except Exception as e:
                print('Error al guardar información:', e)
                return JsonResponse({'success': False, 'error': 'Error al guardar información'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


"""
from urllib.parse import urljoin
from django.conf import settings

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
                # Por cada CircuitIdentity, iterar sus links relacionados
                for link in circuit_identity.link_id.all():
                    nombre = circuit_identity.nombre if circuit_identity.nombre else f'Circuito {link.id}'
                    screenshot_url = link.screenshot.url if link.screenshot else None
                    if screenshot_url:
                        # Armar URL completa para la imagen
                        screenshot_url = urljoin('http://127.0.0.1:8000/' + settings.MEDIA_URL, screenshot_url)

                    circuitos.append({
                        'id': link.id,
                        'url': link.url,
                        'nombre': nombre,
                        'cadena': link.cadena,
                        'url_desplegada': circuit_identity.url_desplegada,
                        'screenshot_url': screenshot_url
                    })

            if not circuitos:
                return JsonResponse({'error': 'No se encontraron circuitos asociados al correo electrónico proporcionado'}, status=404)
            
            return JsonResponse({'circuitos': circuitos})
        
        except Exception as e:
            print('Error al obtener los circuitos:', e)
            return JsonResponse({'error': 'Error al obtener los circuitos'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


"""




@csrf_exempt
def obtener_url_y_nombre_por_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)
        
        try:
            circuit_identities = CircuitIdentity.objects.filter(email=email)
            
            circuit_info = []
            for circuit_identity in circuit_identities:
                print(circuit_identity.link_id, circuit_identity.nombre)
                circuit_info.append({'id': circuit_identity.link_id, 'nombre': circuit_identity.nombre})
            
            circuitos = []
            for circuit in circuit_info:
                try:
                    link = Link.objects.get(id=circuit['id'])
                    nombre = circuit['nombre'] if circuit['nombre'] else f'Circuito {circuit["id"]}'
                    circuit_identity = CircuitIdentity.objects.filter(link_id=circuit['id']).first()
                    screenshot_url = link.screenshot.url if link.screenshot else None
                    if screenshot_url:
                        # Obtener solo la parte de la ruta relevante (después de 'screenshots/')
                        # screenshot_relative_path = screenshot_url.split('screenshots/')[1] if 'screenshots/' in screenshot_url else None
                        # if screenshot_relative_path:
                            screenshot_url = urljoin('http://127.0.0.1:8000/'+settings.MEDIA_URL, screenshot_url)
                    print("Screenshot URL:", screenshot_url)
                    circuitos.append({'id': circuit['id'], 'url': link.url, 'nombre': nombre, 'cadena': link.cadena, 'url_desplegada': circuit_identity.url_desplegada, 'screenshot_url': screenshot_url})  
                except Link.DoesNotExist:
                    pass

            return JsonResponse({'circuitos': circuitos})
        except CircuitIdentity.DoesNotExist:
            return JsonResponse({'error': 'No se encontraron circuitos asociados al correo electrónico proporcionado'}, status=404)
        except Exception as e:
            print('Error al obtener los circuitos:', e)
            return JsonResponse({'error': 'Error al obtener los circuitos'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

"""







# @csrf_exempt
# def obtener_url_y_nombre_por_email(request):
#     if request.method == 'GET':
#         email = request.GET.get('email')
#         if not email:
#             return JsonResponse({'error': 'Se requiere el parámetro email'}, status=400)
        
#         try:
#             # Obtener todos los IDs de circuito asociados al correo electrónico
#             circuit_identities = CircuitIdentity.objects.filter(email=email)
#             circuit_info = []
#             for circuit_identity in circuit_identities:
#                 circuit_info.append({'id': circuit_identity.link_id, 'nombre': circuit_identity.nombre})
            
#             # Obtener las URL, nombres y códigos asociados a los IDs de circuito
#             circuitos = []
#             for circuit in circuit_info:
#                 try:
#                     link = Link.objects.get(id=circuit['id'])
#                     nombre = circuit['nombre'] if circuit['nombre'] else f'Circuito {circuit["id"]}'
#                     circuit_identity = CircuitIdentity.objects.filter(link_id=circuit['id']).first()  # Obtener el objeto CircuitIdentity asociado
                    

#                     circuitos.append({'id': circuit['id'], 'url': link.url, 'nombre': nombre, 'cadena': link.cadena, 'url_desplegada': circuit_identity.url_desplegada})  
#                 except Link.DoesNotExist:
#                     pass

                
#             return JsonResponse({'circuitos': circuitos})
#         except CircuitIdentity.DoesNotExist:
#             return JsonResponse({'error': 'No se encontraron circuitos asociados al correo electrónico proporcionado'}, status=404)
#         except Exception as e:
#             print('Error al obtener los circuitos:', e)
#             return JsonResponse({'error': 'Error al obtener los circuitos'}, status=500)
#     else:
#         return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_nombre_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            link_id = data.get('link_id') 
            nuevo_nombre = data.get('nuevo_nombre')
            print("Link ID:", link_id)
            print("Nuevo nombre:", nuevo_nombre)
            
            # Actualizar el nombre del circuito en la base de datos
            CircuitIdentity.objects.filter(link_id=link_id).update(nombre=nuevo_nombre)
            
            # Devuelve el ID del circuito actualizado junto con la respuesta
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
            print("URL:", url)
            print("ID del circuito:", id_circuito)
            


            # Preparar los datos para la solicitud POST, escapando las comillas internas
            post_data = {"new_url": url}
            headers = {'Content-Type': 'application/json'}
            
            # Hacer una solicitud POST a http://quantumservicesdeployment.spilab.es:8084/new_circuit
            response = requests.post('http://quantumservicesdeployment.spilab.es:8084/new_circuit', json=post_data, headers=headers)



            #  # Escapar las comillas dobles en la URL
            # escaped_url = json.dumps({"new_url": url}, ensure_ascii=False)
            # print("Escaped URL:", escaped_url)
            # # Hacer una solicitud POST a http://quantumservicesdeployment.spilab.es:8084/new_circuit
            # response = requests.post('http://quantumservicesdeployment.spilab.es:8084/new_circuit', json=escaped_url)
            

            # # Hacer una solicitud POST a http://quantumservicesdeployment.spilab.es:8084/new_circuit
            # response = requests.post('http://quantumservicesdeployment.spilab.es:8084/new_circuit', json={'url': url})
            
            # Verificar si la solicitud fue exitosa (código de estado 200)
            if response.status_code == 200:
                # Obtener la URL del servicio del cuerpo de la respuesta
                service_url = response.json().get('path')
                print("URL del servicio:", service_url)

                try:
                    # Actualizar la fila de la base de datos con la URL del servicio
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


@csrf_exempt
def borrar_circuito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            link_id = data.get('link_id') 

            print(f"Intentando borrar -> Email: '{email}', Link ID: '{link_id}'")

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



# @csrf_exempt
# def quitar_link_de_usuario(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             link_id = data.get('link_id')

#             if not email or not link_id:
#                 return JsonResponse({'success': False, 'error 0': 'Email y link_id son requeridos'}, status=400)

#             # Buscar el CircuitIdentity por email
#             circuito = CircuitIdentity.objects.filter(email=email).first()

#             # Buscar el Link
#             link = Link.objects.get(id=link_id)

#             # Remover la relación entre ambos
#             circuito.link_id.remove(link)

#             # Si ya no tiene más links asociados, eliminar el CircuitIdentity (opcional)
#             if circuito.link_id.count() == 0:
#                 circuito.delete()

#             return JsonResponse({'success': True, 'message': 'El link fue removido del usuario correctamente'})

#         except CircuitIdentity.DoesNotExist:
#             return JsonResponse({'success': False, 'error 1': 'CircuitIdentity no encontrado'}, status=404)
#         except Link.DoesNotExist:
#             return JsonResponse({'success': False, 'error 2': 'Link no encontrado'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error 3': str(e)}, status=500)
#     else:
#         return JsonResponse({'error 4': 'Método no permitido'}, status=405)


# @csrf_exempt
# def borrar_circuito(request, id_circuito):
#     if request.method == 'DELETE':
#         try:
#             # Eliminar el circuito de la base de datos
#             circuito = CircuitIdentity.objects.get(link_id=id_circuito)
#             circuito.delete()
#             return JsonResponse({'success': True, 'message': 'Circuito eliminado correctamente'})
#         except CircuitIdentity.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'El circuito no existe'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Método no permitido'}, status=405)

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class CircuitIdentityViewSet(viewsets.ModelViewSet):
    queryset = CircuitIdentity.objects.all()
    serializer_class = CircuitIdentitySerializer
