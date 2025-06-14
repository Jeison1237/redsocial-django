from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password # Para verificar contraseñas hasheadas
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import IntegrityError, transaction # Asegúrate que transaction está importado aquí
from django.urls import reverse
import os # Para manejo de rutas de archivo
from django.conf import settings # Para MEDIA_ROOT
from django.db.models import Q # Asegúrate que Q está importado aquí

from .forms import RegistroUsuarioForm, LoginUsuarioForm, PublicacionForm, ComentarioForm, MensajeForm
from .models import Usuarios , Publicaciones, Megusta, Comentarios, Amistades, Mensajes, Notificaciones

# Importar el decorador personalizado para verificar sesión
def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            # Usar request.path_info para obtener la ruta sin query params
            # o request.get_full_path() si quieres incluir los query params.
            # request.path es también una opción común.
            next_url = request.path_info 
            return redirect(f"{reverse('login_usuario')}?next={next_url}")
        return view_func(request, *args, **kwargs)
    return wrapper
# Vista para la página de inicio
def home(request):
    usuario_id = request.session.get('usuario_id')
    usuario_actual = None
    if usuario_id:
        try:
            usuario_actual = Usuarios.objects.get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            if 'usuario_id' in request.session: del request.session['usuario_id']
            if 'nombre_usuario' in request.session: del request.session['nombre_usuario']
            messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")

    # Prefetch related para optimizar: comentarios y usuario del comentario
    publicaciones_qs = Publicaciones.objects.all().select_related('usuario').prefetch_related('comentarios_set__usuario')
    
    lista_publicaciones_con_datos = []
    comentario_form = ComentarioForm() # Un solo formulario para todos los posts en la plantilla

    for pub in publicaciones_qs:
        if usuario_actual:
            pub.user_has_liked = pub.current_user_has_liked(usuario_actual)
        else:
            pub.user_has_liked = False
        # Los comentarios ya están prefetched y accesibles como pub.comentarios_set.all
        lista_publicaciones_con_datos.append(pub)
        
    context = {
        'mensaje_bienvenida': '¡Bienvenido a la plataforma social definitiva!',
        'usuario_actual': usuario_actual,
        'publicaciones': lista_publicaciones_con_datos,
        'comentario_form': comentario_form, # Pasar el formulario de comentario a la plantilla
    }
    return render(request, 'red_social_app/home.html', context)

# --- Vistas de Autenticación Personalizadas ---
def registro_view(request):
    if request.session.get('usuario_id'): # Si ya está logueado, redirigir
        return redirect('home_redsocial')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES or None) # Añadido request.FILES por si 'foto_perfil' se sube
        if form.is_valid():
            usuario = form.save()
            request.session['usuario_id'] = usuario.pk # Guardar el ID del usuario en la sesión
            request.session['nombre_usuario'] = usuario.nombre # Opcional: guardar más info
            messages.success(request, '¡Registro exitoso! Has iniciado sesión.')
            return redirect('home_redsocial')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'red_social_app/registro.html', {'form': form})

def login_view(request):
    if request.session.get('usuario_id'): # Si ya está logueado, redirigir
        return redirect('home_redsocial')

    if request.method == 'POST':
        form = LoginUsuarioForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo')
            contrasena_ingresada = form.cleaned_data.get('contrasena')
            try:
                usuario = Usuarios.objects.get(correo=correo)
                if check_password(contrasena_ingresada, usuario.contrasena):
                    request.session['usuario_id'] = usuario.pk # Guardar el ID del usuario en la sesión
                    request.session['nombre_usuario'] = usuario.nombre # Opcional
                    messages.info(request, f'¡Bienvenido de nuevo, {usuario.nombre}!')
                    
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('home_redsocial')
                else:
                    # messages.error(request, 'Correo o contraseña incorrectos.') # Comentado o eliminado
                    form.add_error(None, 'Correo o contraseña incorrectos.') # Añadido
            except Usuarios.DoesNotExist:
                # messages.error(request, 'Correo o contraseña incorrectos.') # Comentado o eliminado
                form.add_error(None, 'Correo o contraseña incorrectos.') # Añadido
        else:
            # El formulario no es válido (por ejemplo, campos vacíos)
            # Este mensaje seguirá apareciendo en la parte superior si se deja.
            # Si solo quieres errores de campo, puedes comentar la siguiente línea.
            messages.error(request, 'Por favor, introduce un correo y contraseña válidos.')
    else:
        form = LoginUsuarioForm()
    
    return render(request, 'red_social_app/login.html', {'form': form, 'next': request.GET.get('next', '')})


def logout_view(request):
    # Es mejor que el logout sea por POST para evitar CSRF, pero para simplificar:
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    if 'nombre_usuario' in request.session: # Limpiar también otra info guardada
        del request.session['nombre_usuario']
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login_usuario') # Redirigir al login o a la página de inicio


# --- Vistas de Publicaciones (Placeholders) ---
def crear_publicacion_view(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Debes iniciar sesión para crear una publicación.')
        return redirect('login_usuario' + '?next=' + request.path)
    
    try:
        usuario_actual = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        messages.error(request, "Error: Usuario no encontrado. Por favor, inicia sesión de nuevo.")
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        return redirect('login_usuario')

    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False) # No guardamos aún, url_media es CharField
            publicacion.usuario = usuario_actual
            publicacion.fecha_publicacion = timezone.now()

            # Manejar la subida del archivo para url_media (CharField)
            uploaded_file = form.cleaned_data.get('url_media')
            if uploaded_file:
                # Asegúrate que MEDIA_ROOT está configurado en settings.py
                # Ejemplo: MEDIA_ROOT = BASE_DIR / 'media'
                # Y MEDIA_URL = '/media/'
                # También necesitas añadir static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) a tus urls principales.
                
                # Directorio donde se guardarán las publicaciones dentro de MEDIA_ROOT
                upload_to_dir = 'publicaciones'
                media_publicaciones_path = os.path.join(settings.MEDIA_ROOT, upload_to_dir)
                
                if not os.path.exists(media_publicaciones_path):
                    os.makedirs(media_publicaciones_path, exist_ok=True)

                # Podrías querer generar un nombre de archivo único para evitar colisiones
                # Por simplicidad, usamos el nombre original.
                file_name = uploaded_file.name
                file_path_on_disk = os.path.join(media_publicaciones_path, file_name)
                
                try:
                    with open(file_path_on_disk, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    # Guardar la ruta relativa a MEDIA_ROOT en el CharField del modelo
                    publicacion.url_media = os.path.join(upload_to_dir, file_name).replace("\\", "/")
                except Exception as e:
                    messages.error(request, f"Error al guardar el archivo: {e}")
                    # Decide si continuar sin el archivo o mostrar error y no guardar publicación
                    publicacion.url_media = None # O manejar el error de otra forma

            # Inferir tipo_contenido si no fue provisto explícitamente en el formulario
            tipo_contenido_form = form.cleaned_data.get('tipo_contenido')

            if not tipo_contenido_form: # Si el usuario no especificó un tipo
                if publicacion.url_media and uploaded_file: # Si se guardó un archivo
                    filename_lower = uploaded_file.name.lower()
                    if any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        publicacion.tipo_contenido = 'imagen' # Usar valor exacto del ENUM
                    elif any(filename_lower.endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov', '.avi']):
                        publicacion.tipo_contenido = 'video' # Usar valor exacto del ENUM
                    else:
                        # Si tienes un valor como 'archivo' en tu ENUM y quieres usarlo para otros tipos:
                        # publicacion.tipo_contenido = 'archivo' 
                        # Si no, puedes dejarlo como None si el ENUM y la columna lo permiten,
                        # o asignar un tipo por defecto si es necesario.
                        # Por ahora, si no es imagen o video, y no hay texto, podría quedar None.
                        # Considera si necesitas un tipo 'otro' o 'archivo' en tu ENUM.
                        # Si solo tienes 'texto', 'imagen', 'video', y no es ninguno,
                        # y no hay texto, entonces tipo_contenido podría quedar sin asignar aquí.
                        pass # Se manejará si solo hay texto a continuación
                
                # Esta condición se evalúa después de la de archivo,
                # así que si hay archivo Y texto, el tipo de archivo tiene precedencia.
                # Si solo hay texto (y no archivo), se asigna 'texto'.
                if publicacion.contenido_texto and not publicacion.tipo_contenido:
                    publicacion.tipo_contenido = 'texto' # Usar valor exacto del ENUM
                
                # Si después de todo esto, tipo_contenido sigue siendo None y tu ENUM no lo permite,
                # tendrás un error. Deberías asegurar que siempre se asigne un valor válido del ENUM.
                # Por ejemplo, si no es imagen, ni video, pero hay texto, se pondrá 'texto'.
                # Si no hay ni archivo ni texto, y el ENUM no permite NULL, necesitas un valor por defecto.
                # O si hay un archivo de tipo no reconocido, y no hay texto, también necesitas un valor.

            else:
                # Usar el tipo_contenido que el usuario ingresó en el formulario completo.
                # Es crucial que este valor también coincida con el ENUM.
                # Podrías convertirlo a minúsculas para asegurar consistencia:
                publicacion.tipo_contenido = tipo_contenido_form.strip().lower()
            
            try:
                publicacion.save(using='default')
                messages.success(request, "Publicación creada exitosamente.")
                return redirect('home_redsocial')
            except Exception as e:
                messages.error(request, f"Error al guardar la publicación: {e}")
        else:
            # Construir mensajes de error más detallados
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{form.fields[field].label or field}: {error}")
            if form.non_field_errors():
                 for error in form.non_field_errors():
                    error_messages.append(error)
            messages.error(request, "Por favor corrige los errores: " + "; ".join(error_messages))
    else:
        form = PublicacionForm()

    return render(request, 'red_social_app/crear_publicacion.html', {
        'form': form,
        'usuario_actual': usuario_actual,
        'page_title': 'Crear Nueva Publicación'
    })

@require_POST # Asegura que esta vista solo acepte peticiones POST
def eliminar_publicacion_view(request, publicacion_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para eliminar publicaciones.")
        # Podrías redirigir al login con un 'next' si lo deseas
        return redirect('login_usuario')

    try:
        usuario_actual = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")
        if 'usuario_id' in request.session: del request.session['usuario_id']
        return redirect('login_usuario')

    publicacion = get_object_or_404(Publicaciones, pk=publicacion_id)

    if publicacion.usuario.usuarioid != usuario_actual.usuarioid:
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect(request.META.get('HTTP_REFERER', 'home_redsocial')) # Redirigir a la página anterior o a home

    try:
        # Antes de eliminar la publicación, eliminar las notificaciones asociadas
        Notificaciones.objects.filter(elemento_relacionado_id=publicacion.publicacionid).delete()
        
        # Opcional: Eliminar archivo multimedia asociado si existe
        # if publicacion.url_media:
        #     media_path = os.path.join(settings.MEDIA_ROOT, publicacion.url_media)
        #     if os.path.exists(media_path):
        #         os.remove(media_path)
        
        publicacion.delete()
        messages.success(request, "Publicación y notificaciones asociadas eliminadas exitosamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar la publicación o sus notificaciones: {e}")
    
    return redirect('home_redsocial') # Redirigir a la página de inicio después de eliminar


# --- Vistas de Comentarios (Placeholders) ---
@require_POST # Asegura que esta vista solo acepte peticiones POST
def anadir_comentario_view(request, publicacion_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para comentar.")
        return redirect(f"{reverse('login_usuario')}?next={request.META.get('HTTP_REFERER', reverse('home_redsocial'))}")

    try:
        usuario_actual = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")
        if 'usuario_id' in request.session: del request.session['usuario_id']
        return redirect('login_usuario')

    publicacion = get_object_or_404(Publicaciones, pk=publicacion_id)
    
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.publicacion = publicacion
        comentario.usuario = usuario_actual
        comentario.fecha_comentario = timezone.now()
        try:
            comentario.save(using='default')
            messages.success(request, "Comentario añadido exitosamente.")

            # Crear notificación si el comentario no es del autor de la publicación
            if publicacion.usuario.usuarioid != usuario_actual.usuarioid:
                nombre_notificador = f"{usuario_actual.nombre} {usuario_actual.apellido or ''}".strip()
                Notificaciones.objects.create(
                    usuario_destino_id=publicacion.usuario.usuarioid,
                    tipo_notificacion='nuevo_comentario', # CAMBIADO DE 'comentario'
                    elemento_relacionado_id=publicacion.publicacionid,
                    mensaje_notificacion=f"{nombre_notificador} ha comentado tu publicación.",
                    fecha_creacion=timezone.now(),
                    leida=False
                )
        except IntegrityError: 
            messages.error(request, "No se pudo guardar el comentario. Inténtalo de nuevo.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")
    else:
        error_msg_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msg_list.append(f"{form.fields[field].label or field}: {error}")
        messages.error(request, "Error al añadir comentario: " + "; ".join(error_msg_list))

    redirect_url = request.META.get('HTTP_REFERER', reverse('home_redsocial'))
    if f'#post-{publicacion_id}' not in redirect_url:
        redirect_url += f'#post-{publicacion_id}'
        
    return redirect(redirect_url)

@require_POST # Asegura que esta vista solo acepte peticiones POST
def eliminar_comentario_view(request, publicacion_id, comentario_id): # MODIFICADO: Añadido publicacion_id
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para eliminar comentarios.")
        return redirect('login_usuario')

    try:
        usuario_actual = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")
        if 'usuario_id' in request.session: del request.session['usuario_id']
        return redirect('login_usuario')

    # Usar el publicacion_id de la URL para asegurar que el comentario pertenece a la publicación esperada (opcional pero bueno para consistencia)
    comentario = get_object_or_404(Comentarios, pk=comentario_id, publicacion_id=publicacion_id)
    # publicacion_id_original = comentario.publicacion.publicacionid # Ya tenemos publicacion_id de la URL

    if comentario.usuario.usuarioid != usuario_actual.usuarioid:
        messages.error(request, "No tienes permiso para eliminar este comentario.")
        return redirect(request.META.get('HTTP_REFERER', f"{reverse('home_redsocial')}#post-{publicacion_id}"))

    try:
        comentario.delete() # Esto elimina el comentario de la base de datos
        messages.success(request, "Comentario eliminado exitosamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar el comentario: {e}")
    
    # Redirigir de vuelta a la página anterior, anclando al post
    redirect_url = request.META.get('HTTP_REFERER', reverse('home_redsocial'))
    # Asegurar que el ancla apunte a la publicación correcta usando el publicacion_id de la URL
    if f'#post-{publicacion_id}' not in redirect_url:
        if '#' in redirect_url:
             redirect_url = f"{reverse('home_redsocial')}#post-{publicacion_id}"
        else:
            redirect_url += f'#post-{publicacion_id}'
            
    return redirect(redirect_url)


# --- Vistas de "Me Gusta" (Placeholders) ---
@require_POST # Ensures this view only accepts POST requests
def alternar_megusta_view(request, publicacion_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para interactuar con las publicaciones.")
        return redirect('login_usuario' + '?next=' + request.META.get('HTTP_REFERER', '/redsocial/'))

    try:
        usuario_actual = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")
        if 'usuario_id' in request.session: del request.session['usuario_id']
        return redirect('login_usuario')

    publicacion = get_object_or_404(Publicaciones, pk=publicacion_id)
    
    megusta_existente = Megusta.objects.filter(usuario=usuario_actual, publicacion=publicacion).first()

    if megusta_existente:
        megusta_existente.delete()
        messages.info(request, "Ya no te gusta esta publicación.")
    else:
        try:
            Megusta.objects.create(
                usuario=usuario_actual, 
                publicacion=publicacion,
                fecha_megusta=timezone.now()
            )
            messages.success(request, "¡Te gusta esta publicación!")

            # Crear notificación si el "Me gusta" no es del autor de la publicación
            if publicacion.usuario.usuarioid != usuario_actual.usuarioid:
                nombre_notificador = f"{usuario_actual.nombre} {usuario_actual.apellido or ''}".strip()
                Notificaciones.objects.create(
                    usuario_destino_id=publicacion.usuario.usuarioid,
                    tipo_notificacion='nuevo_megusta', # CAMBIADO DE 'megusta'
                    elemento_relacionado_id=publicacion.publicacionid,
                    mensaje_notificacion=f"{nombre_notificador} le ha dado Me Gusta a tu publicación.",
                    fecha_creacion=timezone.now(),
                    leida=False
                )
        except IntegrityError:
            messages.error(request, "No se pudo procesar tu 'Me gusta'. Inténtalo de nuevo.")
            
    return redirect(request.META.get('HTTP_REFERER', 'home_redsocial'))


# --- Otras Vistas Potenciales (Placeholders) ---
def perfil_usuario_view(request, usuario_id_perfil): # Acepta el ID del usuario del perfil
    perfil_usuario = get_object_or_404(Usuarios, pk=usuario_id_perfil)
    
    current_user_id_session = request.session.get('usuario_id')
    usuario_actual = None
    if current_user_id_session:
        # Es bueno usar get_object_or_404 aquí también por si el ID en sesión es inválido
        usuario_actual = get_object_or_404(Usuarios, pk=current_user_id_session)

    estado_amistad_con_perfil = None
    puede_enviar_solicitud = False
    amistad_obj_para_gestion = None 

    if usuario_actual and usuario_actual.usuarioid != perfil_usuario.usuarioid:
        # Determinar la relación de amistad
        # Q objects para buscar en ambas "direcciones" de la amistad
        relacion = Amistades.objects.filter(
            (Q(usuario1_id=usuario_actual.usuarioid, usuario2_id=perfil_usuario.usuarioid) |
             Q(usuario1_id=perfil_usuario.usuarioid, usuario2_id=usuario_actual.usuarioid))
        ).first() # first() para obtener solo un objeto o None

        if relacion:
            amistad_obj_para_gestion = relacion 
            if relacion.estado_amistad == 'aceptada':
                estado_amistad_con_perfil = 'amigos'
            elif relacion.estado_amistad == 'pendiente':
                if relacion.usuario1_id == usuario_actual.usuarioid: # El usuario actual envió la solicitud
                    estado_amistad_con_perfil = 'solicitud_enviada'
                else: # El usuario actual recibió la solicitud
                    estado_amistad_con_perfil = 'solicitud_recibida'
            elif relacion.estado_amistad == 'rechazada':
                 estado_amistad_con_perfil = 'solicitud_rechazada'
                 # Si fue rechazada, el que la envió originalmente podría querer enviar de nuevo
                 # O si el que la recibió la rechazó, el otro podría enviar.
                 # Por ahora, si está rechazada, permitimos enviar una nueva.
        else: # No existe ninguna relación en la tabla Amistades
            puede_enviar_solicitud = True
    
    # Obtener publicaciones del usuario del perfil y prefetch datos relacionados para eficiencia
    publicaciones_perfil_qs = Publicaciones.objects.filter(usuario=perfil_usuario).select_related('usuario').prefetch_related('comentarios_set__usuario', 'megusta_set')
    
    # Determinar si el usuario_actual ha dado "Me Gusta" a cada publicación del perfil
    for pub in publicaciones_perfil_qs:
        if usuario_actual:
            pub.user_has_liked = pub.current_user_has_liked(usuario_actual)
        else:
            pub.user_has_liked = False

    context = {
        'perfil_usuario': perfil_usuario,
        'publicaciones_perfil': publicaciones_perfil_qs,
        'estado_amistad_con_perfil': estado_amistad_con_perfil,
        'puede_enviar_solicitud': puede_enviar_solicitud,
        'amistad_obj_para_gestion': amistad_obj_para_gestion,
        'usuario_actual': usuario_actual, # El objeto completo del usuario que está viendo la página
        'comentario_form': ComentarioForm(), # Para el formulario de comentarios en las publicaciones
        'page_title': f"Perfil de {perfil_usuario.nombre}"
    }
    return render(request, 'red_social_app/perfil_usuario.html', context)

# --- Vistas de Chat / Mensajería ---

@login_required_custom
def lista_conversaciones_view(request):
    current_user_id = request.session.get('usuario_id')
    usuario_actual = get_object_or_404(Usuarios, pk=current_user_id)

    mensajes_involucrados = Mensajes.objects.filter(
        Q(emisor=usuario_actual) | Q(receptor=usuario_actual)
    ).select_related('emisor', 'receptor').order_by('-fecha_envio')

    conversaciones_dict = {}
    for msg in mensajes_involucrados:
        otro_usuario = msg.receptor if msg.emisor == usuario_actual else msg.emisor
        if otro_usuario.usuarioid not in conversaciones_dict or \
           msg.fecha_envio > conversaciones_dict[otro_usuario.usuarioid]['ultimo_mensaje'].fecha_envio:
            no_leido = (msg.receptor == usuario_actual and msg.fecha_lectura is None)
            conversaciones_dict[otro_usuario.usuarioid] = {
                'usuario': otro_usuario,
                'ultimo_mensaje': msg,
                'no_leido': no_leido 
            }
    
    lista_de_conversaciones_activas = sorted(conversaciones_dict.values(), key=lambda c: c['ultimo_mensaje'].fecha_envio, reverse=True)
    
    # IDs de usuarios con los que ya hay una conversación activa
    ids_usuarios_con_chat_activo = [conv['usuario'].usuarioid for conv in lista_de_conversaciones_activas]

    # Lógica de búsqueda de usuarios para iniciar nuevas conversaciones
    search_query = request.GET.get('q_user_search', '')
    search_results_users = []
    if search_query:
        search_results_users = Usuarios.objects.filter(
            Q(nombre__icontains=search_query) | Q(apellido__icontains=search_query) | Q(correo__icontains=search_query)
        ).exclude(
            usuarioid=current_user_id # Excluir al usuario actual
        ).exclude(
            usuarioid__in=ids_usuarios_con_chat_activo # Excluir usuarios con los que ya hay chat
        ).distinct()[:10] # Limitar a 10 resultados por simplicidad

    context = {
        'usuario_actual': usuario_actual,
        'conversaciones': lista_de_conversaciones_activas, # Renombrado para claridad
        'search_query': search_query,
        'search_results_users': search_results_users,
        'page_title': "Mis Mensajes"
    }
    return render(request, 'red_social_app/lista_conversaciones.html', context)


@login_required_custom
def chat_view(request, receptor_id):
    current_user_id = request.session.get('usuario_id')
    emisor = get_object_or_404(Usuarios, pk=current_user_id)
    receptor = get_object_or_404(Usuarios, pk=receptor_id)

    if emisor == receptor: 
        messages.error(request, "No puedes enviarte mensajes a ti mismo.")
        return redirect('lista_conversaciones') 

    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = emisor
            mensaje.receptor = receptor
            try:
                mensaje.save(using='default') 
                return redirect('chat_con_usuario', receptor_id=receptor.usuarioid) 
            except Exception as e:
                messages.error(request, f"Error al enviar el mensaje: {e}")
    else:
        form = MensajeForm() 

    mensajes_conversacion = Mensajes.objects.filter(
        (Q(emisor=emisor, receptor=receptor) | Q(emisor=receptor, receptor=emisor))
    ).select_related('emisor', 'receptor').order_by('fecha_envio')

    mensajes_no_leidos = Mensajes.objects.filter(
        emisor=receptor, receptor=emisor, fecha_lectura__isnull=True
    )
    # Usar update es más eficiente que iterar y guardar individualmente
    mensajes_no_leidos.update(fecha_lectura=timezone.now(), estado_mensaje='leido')


    context = {
        'usuario_actual': emisor, 
        'receptor_chat': receptor, 
        'mensajes': mensajes_conversacion,
        'form': form, 
        'page_title': f"Chat con {receptor.nombre}"
    }
    return render(request, 'red_social_app/chat_view.html', context)

@login_required_custom
@require_POST 
def enviar_mensaje_view(request, receptor_id):
    current_user_id = request.session.get('usuario_id')
    emisor = get_object_or_404(Usuarios, pk=current_user_id)
    receptor = get_object_or_404(Usuarios, pk=receptor_id)

    if emisor == receptor:
        messages.error(request, "No puedes enviarte mensajes a ti mismo.")
        return redirect('lista_conversaciones') 

    form = MensajeForm(request.POST)
    if form.is_valid():
        mensaje = form.save(commit=False)
        mensaje.emisor = emisor
        mensaje.receptor = receptor
        try:
            mensaje.save(using='default')
        except Exception as e:
            messages.error(request, f"Error al enviar el mensaje: {e}")
    else:
        for field, errors_list in form.errors.items():
            for error in errors_list:
                messages.error(request, f"{form.fields[field].label or field}: {error}")
                
    return redirect('chat_con_usuario', receptor_id=receptor.usuarioid)


@login_required_custom
def amigos_view(request):
    current_user_id = request.session.get('usuario_id')
    usuario_actual_obj = get_object_or_404(Usuarios, pk=current_user_id)
    
    # 1. Amigos Aceptados
    amistades_aceptadas_qs = Amistades.objects.filter(
        (Q(usuario1_id=current_user_id) | Q(usuario2_id=current_user_id)),
        estado_amistad='aceptada'
    ).select_related('usuario1', 'usuario2')

    friends_list_users = []
    for amistad in amistades_aceptadas_qs:
        if amistad.usuario1_id == current_user_id:
            friends_list_users.append(amistad.usuario2) 
        else:
            friends_list_users.append(amistad.usuario1) 
            
    # 2. Solicitudes de Amistad Recibidas
    incoming_requests_data = []
    incoming_qs = Amistades.objects.filter(
        usuario2_id=current_user_id, 
        estado_amistad='pendiente'
    ).select_related('usuario1') 
    
    for req in incoming_qs:
        incoming_requests_data.append({
            'amistad_obj': req, 
            'solicitante': req.usuario1 
        })
    
    # 3. Solicitudes de Amistad Enviadas
    outgoing_requests_data = []
    outgoing_qs = Amistades.objects.filter(
        usuario1_id=current_user_id, 
        estado_amistad='pendiente'
    ).select_related('usuario2')

    for req in outgoing_qs:
        outgoing_requests_data.append({
            'amistad_obj': req, 
            'destinatario': req.usuario2 
        })

    # 4. Búsqueda de Usuarios
    search_query = request.GET.get('q_user_search', '')
    search_results_with_status = []

    if search_query:
        # Excluir al usuario actual de los resultados de búsqueda
        search_results_qs = Usuarios.objects.filter(
            Q(nombre__icontains=search_query) | Q(apellido__icontains=search_query)
        ).exclude(usuarioid=current_user_id).distinct()

        for found_user in search_results_qs:
            status = 'puede_enviar_solicitud' # Default status
            amistad_obj_for_action = None
            
            # Verificar si existe una relación con el usuario encontrado
            relacion = Amistades.objects.filter(
                (Q(usuario1=usuario_actual_obj, usuario2=found_user) | 
                 Q(usuario1=found_user, usuario2=usuario_actual_obj))
            ).first()

            if relacion:
                amistad_obj_for_action = relacion
                if relacion.estado_amistad == 'aceptada':
                    status = 'amigos'
                elif relacion.estado_amistad == 'pendiente':
                    if relacion.usuario1 == usuario_actual_obj: # El usuario actual envió la solicitud
                        status = 'solicitud_enviada'
                    else: # El usuario actual recibió la solicitud (found_user es usuario1)
                        status = 'solicitud_recibida'
                elif relacion.estado_amistad == 'rechazada':
                    # Si fue rechazada, se considera que puede enviar una nueva
                    status = 'puede_enviar_solicitud' # O un estado específico como 'solicitud_rechazada_puede_reenviar'

            search_results_with_status.append({
                'user': found_user,
                'status': status,
                'amistad_obj': amistad_obj_for_action
            })

    context = {
        'friends_list': friends_list_users, 
        'incoming_requests': incoming_requests_data,
        'outgoing_requests': outgoing_requests_data,
        'search_query': search_query,
        'search_results_users_with_status': search_results_with_status,
        'page_title': 'Mis Amigos'
    }
    return render(request, 'red_social_app/amigos.html', context)

# --- Vistas de Notificaciones ---
@login_required_custom
def notificaciones_view(request):
    usuario_id = request.session.get('usuario_id')
    
    notificaciones = Notificaciones.objects.filter(
        usuario_destino_id=usuario_id
    ).order_by('-fecha_creacion')

    context = {
        'notificaciones_todas': notificaciones,
        'page_title': 'Mis Notificaciones',
        'usuario_actual': get_object_or_404(Usuarios, pk=usuario_id) if usuario_id else None
    }
    return render(request, 'red_social_app/notificaciones.html', context)

@login_required_custom
def marcar_notificacion_leida_y_redirigir(request, notificacion_id):
    usuario_id = request.session.get('usuario_id')
    notificacion = get_object_or_404(Notificaciones, pk=notificacion_id, usuario_destino_id=usuario_id)

    # Marcar la notificación como leída
    if notificacion.leida:
        notificacion.leida = True
        notificacion.save(update_fields=['leida'])

    # Redirigir a la publicación si es una notificación de 'megusta' o 'comentario'
    # ACTUALIZAR TAMBIÉN AQUÍ SI ES NECESARIO PARA LA LÓGICA DE REDIRECCIÓN
    if notificacion.tipo_notificacion in ['nuevo_megusta', 'nuevo_comentario'] and notificacion.elemento_relacionado_id:
        try:
            publicacion = Publicaciones.objects.get(pk=notificacion.elemento_relacionado_id)
            return redirect(reverse('home_redsocial') + f'#post-{publicacion.publicacionid}')
        except Publicaciones.DoesNotExist:
            messages.error(request, "La publicación relacionada con esta notificación ya no existe.")
            return redirect('notificaciones') 
    
    # Eliminar la notificación
    notificacion.delete()
    
    return redirect('notificaciones')

# --- Vistas de Amistades (Placeholders) ---

@login_required_custom
@require_POST 
def send_friend_request_view(request, recipient_usuario_id):
    # Asegúrate de que el usuario actual esté logueado (ya cubierto por el decorador)
    sender_usuario_id = request.session.get('usuario_id')
    sender_usuario = get_object_or_404(Usuarios, pk=sender_usuario_id)
    recipient_usuario = get_object_or_404(Usuarios, pk=recipient_usuario_id)

    # Redirigir a la página anterior o al perfil del destinatario
    redirect_url = request.META.get('HTTP_REFERER', reverse('perfil_usuario', args=[recipient_usuario_id]))

    if sender_usuario.usuarioid == recipient_usuario.usuarioid:
        messages.error(request, "No puedes enviarte una solicitud de amistad a ti mismo.")
        return redirect(redirect_url)

    try:
        with transaction.atomic(using='default'):
            # Verificar si ya existe una relación o solicitud en cualquier dirección
            existing_relation = Amistades.objects.filter(
                (Q(usuario1_id=sender_usuario.usuarioid, usuario2_id=recipient_usuario.usuarioid) |
                 Q(usuario1_id=recipient_usuario.usuarioid, usuario2_id=sender_usuario.usuarioid))
            ).first()

            if existing_relation:
                if existing_relation.estado_amistad == 'aceptada':
                    messages.info(request, f"Ya eres amigo de {recipient_usuario.nombre}.")
                elif existing_relation.estado_amistad == 'pendiente':
                    if existing_relation.usuario1_id == sender_usuario.usuarioid:
                        messages.info(request, f"Ya has enviado una solicitud a {recipient_usuario.nombre}.")
                    else: # El usuario actual recibió la solicitud, puedes aceptarla
                        messages.info(request, f"{recipient_usuario.nombre} ya te ha enviado una solicitud. Puedes aceptarla desde la página de Amigos o su perfil.")
                elif existing_relation.estado_amistad == 'rechazada':
                    # Si fue rechazada, actualizamos para reenviar (el que envía ahora es el sender_usuario)
                    existing_relation.usuario1_id = sender_usuario.usuarioid
                    existing_relation.usuario2_id = recipient_usuario.usuarioid
                    existing_relation.estado_amistad = 'pendiente'
                    existing_relation.fecha_solicitud = timezone.now()
                    existing_relation.fecha_aceptacion = None # Limpiar fecha de aceptación si la hubo
                    existing_relation.save(using='default')
                    messages.success(request, f"Solicitud de amistad reenviada a {recipient_usuario.nombre}.")
                return redirect(redirect_url)

            # Si no hay relación, crear una nueva solicitud pendiente
            Amistades.objects.create(
                usuario1_id=sender_usuario.usuarioid,
                usuario2_id=recipient_usuario.usuarioid,
                estado_amistad='pendiente',
                fecha_solicitud=timezone.now()
            )
            messages.success(request, f"Solicitud de amistad enviada a {recipient_usuario.nombre}.")

    except IntegrityError: # Podría ocurrir si hay una constraint unique_together que no consideramos bien
        messages.error(request, "No se pudo enviar la solicitud. Puede que ya exista una relación o una solicitud pendiente.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado al enviar la solicitud: {e}")
        
    return redirect(redirect_url)

@login_required_custom
@require_POST
def manage_friend_request_view(request, amistad_id, action):
    current_user_id = request.session.get('usuario_id')
    # La solicitud debe ser para el current_user (él es usuario2) y estar pendiente
    # Nota: El modelo Amistades tiene usuario1_id y usuario2_id
    friend_request = get_object_or_404(Amistades, pk=amistad_id, usuario2_id=current_user_id, estado_amistad='pendiente')
    
    # Obtener el objeto del solicitante para mensajes y posible redirección
    solicitante = get_object_or_404(Usuarios, pk=friend_request.usuario1_id)
    redirect_page = request.META.get('HTTP_REFERER', reverse('amigos')) # Redirigir a 'amigos' o a la página anterior

    try:
        with transaction.atomic(using='default'):
            if action == 'accept':
                friend_request.estado_amistad = 'aceptada'
                friend_request.fecha_aceptacion = timezone.now()
                friend_request.save(using='default')
                messages.success(request, f"Has aceptado la solicitud de amistad de {solicitante.nombre}.")
            elif action == 'reject':
                friend_request.estado_amistad = 'rechazada' 
                # Opcional: friend_request.delete(using='default') si prefieres eliminarla de la DB
                friend_request.save(using='default') # Guardar el estado 'rechazada'
                messages.info(request, f"Has rechazado la solicitud de amistad de {solicitante.nombre}.")
            else:
                messages.error(request, "Acción no válida.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al gestionar la solicitud: {e}")

    return redirect(redirect_page)

@login_required_custom
@require_POST
def remove_friend_view(request, friend_usuario_id):
    current_user_id = request.session.get('usuario_id')
    # Redirigir a la página anterior o a la página de amigos por defecto
    redirect_page = request.META.get('HTTP_REFERER', reverse('amigos')) 

    if current_user_id == friend_usuario_id: # Comparamos IDs
        messages.error(request, "Acción no válida.")
        return redirect(redirect_page)

    try:
        with transaction.atomic(using='default'):
            # Buscar la amistad aceptada entre el usuario actual y el amigo a eliminar
            amistad = Amistades.objects.filter(
                (Q(usuario1_id=current_user_id, usuario2_id=friend_usuario_id) | 
                 Q(usuario1_id=friend_usuario_id, usuario2_id=current_user_id)),
                estado_amistad='aceptada'
            ).first()

            if amistad:
                # En lugar de cambiar el estado, eliminamos la fila para "deshacer" la amistad
                amistad.delete(using='default')
                friend_to_remove_obj = get_object_or_404(Usuarios, pk=friend_usuario_id) # Para el mensaje
                messages.success(request, f"Has eliminado a {friend_to_remove_obj.nombre} de tus amigos.")
            else:
                messages.error(request, "No se encontró la relación de amistad para eliminar.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar al amigo: {e}")
    
    return redirect(redirect_page)
