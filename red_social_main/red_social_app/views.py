from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password # Para verificar contraseñas hasheadas

from .forms import RegistroUsuarioForm, LoginUsuarioForm, PublicacionForm # Nuestros formularios personalizados
from .models import Usuarios , Publicaciones# Nuestro modelo de usuario


# Vista para la página de inicio
def home(request):
    usuario_id = request.session.get('usuario_id')
    usuario_actual = None
    if usuario_id:
        try:
            usuario_actual = Usuarios.objects.get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            # El usuario_id en la sesión no es válido, limpiar sesión
            del request.session['usuario_id']
            messages.error(request, "Error de sesión. Por favor, inicia sesión de nuevo.")

    lista_publicaciones = Publicaciones.objects.all() # Esto usa el 'ordering' definido en el modelo    
    context = {
        'mensaje_bienvenida': '¡Bienvenido a la plataforma social definitiva!',
        'usuario_actual': usuario_actual,
        'publicaciones': lista_publicaciones, # Pasar las publicaciones a la plantilla
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
            request.session['nombre_usuario'] = usuario.nombre_usuario # Opcional: guardar más info
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
                    request.session['nombre_usuario'] = usuario.nombre_usuario # Opcional
                    messages.info(request, f'¡Bienvenido de nuevo, {usuario.nombre_usuario}!')
                    
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('home_redsocial')
                else:
                    messages.error(request, 'Correo o contraseña incorrectos.')
            except Usuarios.DoesNotExist:
                messages.error(request, 'Correo o contraseña incorrectos.')
        else:
            # El formulario no es válido (por ejemplo, campos vacíos)
            messages.error(request, 'Por favor, introduce un correo y contraseña válidos.')
    else:
        form = LoginUsuarioForm()
    
    # Pasar 'next' a la plantilla para que el formulario pueda redirigir correctamente
    # La plantilla de login debería tener un <input type="hidden" name="next" value="{{ request.GET.next }}">
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
            publicacion = form.save(commit=False)
            publicacion.usuario = usuario_actual  # Relación correcta
            publicacion.save(using='default')     # Explicitamente usando la base de datos por si tienes varias
            messages.success(request, "Publicación creada exitosamente.")
            return redirect('home_redsocial')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = PublicacionForm()

    return render(request, 'red_social_app/crear_publicacion.html', {
        'form': form,
        'usuario_actual': usuario_actual,
        'page_title': 'Crear Nueva Publicación'
    })


# (El resto de tus vistas placeholder pueden permanecer igual por ahora)
# --- Vistas de Comentarios (Placeholders) ---
# @login_required
def anadir_comentario_view(request, publicacion_id):
    return HttpResponse(f"Placeholder para añadir comentario a la publicación ID: {publicacion_id}")

# --- Vistas de "Me Gusta" (Placeholders) ---
# @login_required
def alternar_megusta_view(request, publicacion_id):
    return HttpResponse(f"Placeholder para alternar 'Me Gusta' en la publicación ID: {publicacion_id}")


# --- Otras Vistas Potenciales (Placeholders) ---
def perfil_usuario_view(request, nombre_usuario):
    return HttpResponse(f"Placeholder para el perfil del usuario: {nombre_usuario}")

def mensajes_view(request):
    return HttpResponse("Placeholder para la sección de Mensajes")

def amigos_view(request):
    return HttpResponse("Placeholder para la sección de Amigos")

def notificaciones_view(request):
    return HttpResponse("Placeholder para la sección de Notificaciones")