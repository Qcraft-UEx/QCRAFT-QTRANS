"""
URL configuration for djangobd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from link import views as link_views
from circuitIdentity import views as ci_views
from results import views as results_views
from results_debug import views as results_debug_views
from deployment import views as deployment_views
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'links', link_views.LinkViewSet)
router.register(r'circuitIdentity', ci_views.CircuitIdentityViewSet)
router.register(r'results', results_views.ResultsViewSet)
router.register(r'resultsDebug', results_debug_views.ResultsDebugViewSet)
router.register(r'deployment', deployment_views.DeploymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recibir_url_quirk/', link_views.recibir_url_quirk,
         name='recibir_url_quirk'),
         
    # --- NUEVA RUTA PARA LA API DE TRADUCCIÓN ---
    path('api/translate/', link_views.translate_circuit_api, name='translate_api'),
    # --------------------------------------------
    
    path('get_id_from_cadena/', link_views.get_id_from_cadena,
         name='get_id_from_cadena'),
    path('actualizar_url_circuito/', link_views.actualizar_url_circuito,
         name='actualizar_url_circuito'),
    path('guardar_info/', ci_views.guardar_info, name='guardar_info'),
    path('obtener_url_y_nombre_por_email/', ci_views.obtener_url_y_nombre_por_email,
         name='obtener_url_y_nombre_por_email'),
    path('actualizar_nombre_circuito/', ci_views.actualizar_nombre_circuito,
         name='actualizar_nombre_circuito'),
    path('lanzar_servicio/', ci_views.lanzar_servicio, name='lanzar_servicio'),
    path('circuitos/borrar_circuito/', ci_views.borrar_circuito, name='borrar_circuito'),
    path('obtener_nombres_circuitos_por_email/', results_views.obtener_nombres_circuitos_por_email,
         name='obtener_nombres_circuitos_por_email'),
    path('obtener_resultados_circuito/', results_views.obtener_resultados_circuito,
         name='obtener_resultados_circuito'),
    path('resultados/borrar/<int:id_resultado>/',
         results_views.borrar_resultado, name='borrar_resultado'),
    path('ejecutar_circuito/', results_views.ejecutar_circuito,
         name='ejecutar_circuito'),
    path('check_task_result/', results_views.check_task_result,
         name='check_task_result'),
    path('check_circuit_exists/', results_debug_views.check_circuit_exists,
         name='check_circuit_exists'),
    path('get_csrf_token/', ci_views.get_csrf_token, name='get_csrf_token'),
    path('create_update/', deployment_views.create_update, name='create_update'),
    path('recuperar_info/<str:email>/',
         deployment_views.recuperar_info, name='recuperar_info'),
    path('', include(router.urls)),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)