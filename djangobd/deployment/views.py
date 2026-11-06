from django.shortcuts import render
from rest_framework import viewsets
from .models import Deployment
from django.http import JsonResponse
from .models import Deployment
from .serializers import DeploymentSerializer
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
import json
from rest_framework.response import Response
from rest_framework import status


@csrf_exempt
def create_update(request):
    if request.method == 'POST':
        # Acceder a los datos enviados en la solicitud POST
        data = json.loads(request.body)
        email = data.get('email')
        public_AWS = data.get('public_AWS')
        private_AWS = data.get('private_AWS')
        folder_AWS = data.get('s3_folder')
        clave_IBM = data.get('clave_IBM')

        # Verificar si ya existe un Deployment con el correo electrónico dado
        deployment_queryset = Deployment.objects.filter(email=email)
        if deployment_queryset.exists():
            # Si hay un Deployment existente, actualiza sus campos
            deployment = deployment_queryset.first()
            deployment.public_AWS = public_AWS
            deployment.private_AWS = private_AWS
            deployment.s3_AWS = folder_AWS
            deployment.token_IBM = clave_IBM
            deployment.save()
            return JsonResponse({'message': 'Deployment actualizado correctamente'}, status=status.HTTP_200_OK)
        else:
            # Si no hay un Deployment existente, créalo
            deployment = Deployment.objects.create(email=email, public_AWS=public_AWS, private_AWS=private_AWS, s3_AWS=folder_AWS ,token_IBM=clave_IBM)
            return JsonResponse({'message': 'Deployment creado correctamente'}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@csrf_exempt
def recuperar_info(request, email):
    if request.method == 'GET':
        try:
            deployment = Deployment.objects.get(email=email)
            # Devolver un diccionario de Python convertido a JSON
            return JsonResponse({
                'email': deployment.email,
                'public_AWS': deployment.public_AWS,
                'private_AWS': deployment.private_AWS,
                'folder_AWS': deployment.s3_AWS,
                'clave_IBM': deployment.token_IBM
            })
        except Deployment.DoesNotExist:
            # Devolver un diccionario vacío si no se encuentra ningún despliegue
            return JsonResponse({})
    else:
        # Utilizar HttpResponseNotAllowed para manejar los métodos no permitidos
        return HttpResponseNotAllowed(['GET'])




# Create your views here.
class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
