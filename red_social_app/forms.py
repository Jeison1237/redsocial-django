from django import forms
from .models import Usuarios, Publicaciones, Comentarios, Mensajes # Añadir Comentarios
from django.contrib.auth.hashers import make_password

class RegistroUsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuarios
        # Campos ajustados: 'nombre_usuario' y 'biografia' eliminados
        fields = ['nombre', 'apellido', 'correo', 'contrasena', 'confirmar_contrasena', 'foto_perfil'] 
        # También podrías quitar 'foto_perfil' si es opcional y se añade después del registro.

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuarios.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo

    # Si eliminaste 'nombre_usuario' del formulario, también puedes eliminar esta validación:
    # def clean_nombre_usuario(self):
    #     nombre_usuario = self.cleaned_data.get('nombre_usuario')
    #     if Usuarios.objects.filter(nombre_usuario=nombre_usuario).exists():
    #         raise forms.ValidationError("Este nombre de usuario ya está en uso.")
    #     return nombre_usuario

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            self.add_error('confirmar_contrasena', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.contrasena = make_password(self.cleaned_data["contrasena"])
        if commit:
            user.save()
        return user

class LoginUsuarioForm(forms.Form):
    correo = forms.EmailField(label="Correo Electrónico")
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

class PublicacionForm(forms.ModelForm):
    # Sobrescribir url_media para tratarlo como subida de archivo en el formulario
    url_media = forms.FileField(required=False, label="Archivo adjunto")

    class Meta:
        model = Publicaciones
        fields = ['contenido_texto', 'url_media', 'tipo_contenido']
        widgets = {
            'contenido_texto': forms.Textarea(attrs={
                'class': 'create-post-textarea',
                'placeholder': '¿Qué estás pensando?'
            }),
            'tipo_contenido': forms.TextInput(attrs={ # El usuario aún puede escribirlo si usa el form completo
                'placeholder': 'Ej: IMAGEN, VIDEO, TEXTO (opcional)'
            }),
            # No necesitamos widget para url_media aquí, FileField tiene uno por defecto.
        }
        labels = {
            'contenido_texto': 'Contenido',
            # 'url_media' ya tiene label de la definición del campo arriba
            'tipo_contenido': 'Tipo de contenido (opcional)',
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentarios
        fields = ['contenido_comentario']
        widgets = {
            'contenido_comentario': forms.Textarea(attrs={
                'rows': 2, 
                'placeholder': 'Escribe un comentario...',
                'class': 'form-control form-control-sm' # Añade clases si usas Bootstrap o similar
            }),
        }
        labels = {
            'contenido_comentario': '', # Opcional: puedes quitar la etiqueta si el placeholder es suficiente
        }

    # Nuevo formulario para enviar mensajes
class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensajes
        fields = ['contenido_mensaje'] # Solo necesitamos el campo del contenido del mensaje
        widgets = {
            'contenido_mensaje': forms.Textarea(attrs={
                'rows': 1, # Empezar con 1 fila, puede crecer con CSS o JS si es necesario
                'placeholder': 'Escribe un mensaje...',
                'class': 'form-control chat-message-input', # Clase específica para estilos
                'aria-label': 'Contenido del mensaje' # Para accesibilidad
            }),
        }
        labels = {
            'contenido_mensaje': '', # No mostrar etiqueta, el placeholder es suficiente
        }