from django.db import models
from django.utils import timezone # Import timezone
from django.conf import settings # Importar settings

class Usuarios(models.Model):
    usuarioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    correo = models.CharField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255, db_column='contraseña')  # ¡OJO! La columna real es 'contraseña'
    fecha_nacimiento = models.DateField(blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/',max_length=512, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    ultima_conexion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''} ({self.correo})".strip()


class Publicaciones(models.Model):
    publicacionid = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    contenido_texto = models.TextField(blank=True, null=True)
    url_media = models.CharField(max_length=512, blank=True, null=True)
    tipo_contenido = models.CharField(max_length=50, blank=True, null=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publicaciones'
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return f"Publicación ({self.publicacionid}) por {self.usuario.nombre}"

    @property
    def total_megusta(self):
        """Retorna el número total de 'Me gusta' para esta publicación."""
        return self.megusta_set.count()

    def current_user_has_liked(self, current_user_obj):
        """
        Verifica si el usuario actual (pasado como objeto Usuarios)
        le ha dado 'Me gusta' a esta publicación.
        """
        if current_user_obj and isinstance(current_user_obj, Usuarios):
            return self.megusta_set.filter(usuario=current_user_obj).exists()
        return False

    @property
    def total_comentarios(self):
        """Retorna el número total de comentarios para esta publicación."""
        return self.comentarios_set.count() # Asume related_name es 'comentarios_set' o por defecto

    @property
    def get_media_url(self):
        """Retorna la URL completa del archivo media si existe."""
        if self.url_media:
            media_url = settings.MEDIA_URL if settings.MEDIA_URL.endswith('/') else f"{settings.MEDIA_URL}/"
            media_path = self.url_media.lstrip('/') if media_url.endswith('/') and self.url_media.startswith('/') else self.url_media
            return f"{media_url}{media_path}"
        return None

class Comentarios(models.Model):
    comentarioid = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    contenido_comentario = models.TextField()
    fecha_comentario = models.DateTimeField(blank=True, null=True) # La vista se encargará de poner la fecha
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comentarios'
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['fecha_comentario'] # Ordenar comentarios por fecha

    def __str__(self):
        return f"Comentario ({self.comentarioid}) de {self.usuario.nombre} en Pub ({self.publicacion.publicacionid})"


class Megusta(models.Model):
    megustaid = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    fecha_megusta = models.DateTimeField(default=timezone.now, blank=True, null=True) # Ensure fecha_megusta can be set

    class Meta:
        managed = False
        db_table = 'megusta'
        unique_together = (('usuario', 'publicacion'),)
        verbose_name = "Me Gusta"
        verbose_name_plural = "Me Gusta"

    def __str__(self):
        return f"{self.usuario.nombre} le gusta Pub ({self.publicacion.publicacionid})"


class Notificaciones(models.Model):
    notificacionid = models.AutoField(primary_key=True)
    usuario_destino_id = models.IntegerField(db_column='usuario_destino_id') 
    tipo_notificacion = models.CharField(max_length=100, blank=True, null=True) 
    elemento_relacionado_id = models.IntegerField(blank=True, null=True) 
    mensaje_notificacion = models.CharField(max_length=500)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(blank=True, null=True) 

    class Meta:
        managed = False
        db_table = 'notificaciones'
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notif ({self.notificacionid}) para Usuario ID {self.usuario_destino_id}: {self.mensaje_notificacion[:50]}"

class Amistades(models.Model):
    amistadid = models.AutoField(primary_key=True)
    # El campo del modelo se llama 'usuario1', pero en la BD la columna es 'usuario1_id'
    usuario1 = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='usuario1_id', related_name='amistades_iniciadas')
    # El campo del modelo se llama 'usuario2', pero en la BD la columna es 'usuario2_id'
    usuario2 = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='usuario2_id', related_name='amistades_recibidas')
    estado_amistad = models.CharField(max_length=50, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(blank=True, null=True)
    fecha_aceptacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'amistades'
        unique_together = (('usuario1', 'usuario2'),) 
        verbose_name = "Amistad"
        verbose_name_plural = "Amistades"

    def __str__(self):
        return f"Amistad {self.amistadid}: {self.usuario1_id} -> {self.usuario2_id} ({self.estado_amistad})"


class Mensajes(models.Model):
    mensajeid = models.AutoField(primary_key=True)
    # Cambiamos IntegerField por ForeignKey y especificamos el nombre de la columna en la BD
    emisor = models.ForeignKey(Usuarios, models.CASCADE, db_column='emisor_id', related_name='mensajes_enviados')
    receptor = models.ForeignKey(Usuarios, models.CASCADE, db_column='receptor_id', related_name='mensajes_recibidos')
    contenido_mensaje = models.TextField()
    # Establecemos un valor predeterminado para fecha_envio
    fecha_envio = models.DateTimeField(default=timezone.now, blank=True, null=True)
    fecha_lectura = models.DateTimeField(blank=True, null=True)
    # Establecemos un valor predeterminado para estado_mensaje
    estado_mensaje = models.CharField(max_length=50, blank=True, null=True, default='enviado') # Ej: 'enviado', 'leido', 'fallido'

    class Meta:
        managed = False # Mantenemos esto ya que tu esquema de BD probablemente es fijo
        db_table = 'mensajes'
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['fecha_envio'] # Ordenar mensajes cronológicamente

    def __str__(self):
        # Asegurarse de que emisor y receptor están cargados para evitar errores si no lo están
        emisor_nombre = self.emisor.nombre if self.emisor else "Desconocido"
        receptor_nombre = self.receptor.nombre if self.receptor else "Desconocido"
        return f"Mensaje ({self.mensajeid}) de {emisor_nombre} a {receptor_nombre}"