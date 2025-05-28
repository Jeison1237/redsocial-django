from django.urls import path
from . import views

# El nombre 'app_name' es opcional pero puede ser útil para namespacing si tienes múltiples apps
# app_name = 'red_social_app' 

urlpatterns = [
    # URLs principales de la aplicación
    path('', views.home, name='home_redsocial'),
    
    # URLs para Publicaciones
    path('publicar/', views.crear_publicacion_view, name='crear_publicacion'),
    
    # URLs para Comentarios (asociados a una publicación)
    path('publicacion/<int:publicacion_id>/comentar/', views.anadir_comentario_view, name='anadir_comentario'),
    
    # URLs para "Me Gusta" (asociados a una publicación)
    path('publicacion/<int:publicacion_id>/megusta/', views.alternar_megusta_view, name='alternar_megusta'),
    
    # URLs para el sistema de Autenticación (las vistas se crearán más adelante)
    path('registro/', views.registro_view, name='registro_usuario'), 
    path('login/', views.login_view, name='login_usuario'),
    path('logout/', views.logout_view, name='logout_usuario'),
    
    # Aquí podrías añadir más URLs a medida que desarrolles más funcionalidades:
    # path('perfil/<str:nombre_usuario>/', views.perfil_usuario_view, name='perfil_usuario'),
    # path('mensajes/', views.mensajes_view, name='mensajes'),
    # path('amigos/', views.amigos_view, name='amigos'),
    # path('notificaciones/', views.notificaciones_view, name='notificaciones'),
]