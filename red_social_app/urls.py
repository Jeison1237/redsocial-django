from django.urls import path
from . import views

# El nombre 'app_name' es opcional pero puede ser útil para namespacing si tienes múltiples apps
# app_name = 'red_social_app' 

urlpatterns = [
    # URLs principales de la aplicación
    path('', views.home, name='home_redsocial'),
    
    # URLs para Publicaciones
    path('publicar/', views.crear_publicacion_view, name='crear_publicacion'),
    path('publicacion/<int:publicacion_id>/eliminar/', views.eliminar_publicacion_view, name='eliminar_publicacion'), 
    
    # URLs para Comentarios (asociados a una publicación)
    path('publicacion/<int:publicacion_id>/comentar/', views.anadir_comentario_view, name='anadir_comentario'),
    path('publicacion/<int:publicacion_id>/comentario/<int:comentario_id>/eliminar/', views.eliminar_comentario_view, name='eliminar_comentario'),
    path('publicacion/<int:publicacion_id>/megusta/', views.alternar_megusta_view, name='alternar_megusta'),
    
    # URLs de Notificaciones
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('notificacion/<int:notificacion_id>/leer/', views.marcar_notificacion_leida_y_redirigir, name='leer_notificacion'),

    # URLs para el sistema de Autenticación (las vistas se crearán más adelante)
    path('registro/', views.registro_view, name='registro_usuario'),
    path('login/', views.login_view, name='login_usuario'),
    path('logout/', views.logout_view, name='logout_usuario'),
    
    # URLs para Mensajes/Chat --- NUEVAS ---
    path('mensajes/', views.lista_conversaciones_view, name='lista_conversaciones'), # Para listar todas las conversaciones
    path('mensajes/<int:receptor_id>/', views.chat_view, name='chat_con_usuario'), # Para una conversación específica
    path('mensajes/enviar/<int:receptor_id>/', views.enviar_mensaje_view, name='enviar_mensaje'), # Para enviar un mensaje (puede ser manejado por chat_view)
    # Otras URLs de la aplicación (ejemplos)
    path('perfil/<int:usuario_id_perfil>/', views.perfil_usuario_view, name='perfil_usuario'),
    path('amigos/', views.amigos_view, name='amigos'),

    path('amistad/enviar/<int:recipient_usuario_id>/', views.send_friend_request_view, name='send_friend_request'),
    path('amistad/gestionar/<int:amistad_id>/<str:action>/', views.manage_friend_request_view, name='manage_friend_request'),
    path('amistad/eliminar/<int:friend_usuario_id>/', views.remove_friend_view, name='remove_friend'),
]