from .models import Usuarios # Asegúrate de que la importación de tu modelo Usuarios sea correcta

def datos_usuario_actual(request):
    usuario_actual = None
    usuario_id = request.session.get('usuario_id') # Obtiene el ID de la sesión

    if usuario_id:
        try:
            # Busca el usuario en tu tabla Usuarios usando el ID de la sesión
            usuario_actual = Usuarios.objects.get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            # Si el usuario_id en la sesión no corresponde a un usuario real (quizás fue eliminado),
            # es buena idea limpiar la sesión para evitar problemas.
            if 'usuario_id' in request.session:
                del request.session['usuario_id']
            # También limpia cualquier otro dato de usuario que hayas guardado en la sesión
            if 'nombre_usuario' in request.session: 
                del request.session['nombre_usuario']
            # Puedes añadir más claves de sesión para limpiar si es necesario
            
    # Devuelve un diccionario. La clave 'usuario_actual' estará disponible en tus plantillas.
    return {'usuario_actual': usuario_actual}
