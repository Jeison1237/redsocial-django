from django.db import models
# from django.contrib.auth.models import AbstractUser # Considera esto para Usuarios si quieres integrar con el sistema de auth de Django

# Es buena práctica definir ENUMs o CHOICES si tus campos de texto como 'estado_amistad', 'tipo_notificacion', etc.,
# realmente representan un conjunto limitado de opciones.
# Ejemplo:
# class EstadoAmistad(models.TextChoices):
#     PENDIENTE = 'PENDIENTE', 'Pendiente'
#     ACEPTADA = 'ACEPTADA', 'Aceptada'
#     RECHAZADA = 'RECHAZADA', 'Rechazada'
#     BLOQUEADA = 'BLOQUEADA', 'Bloqueada'

class Usuarios(models.Model):
    usuarioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100) # Asumimos que nombre no puede ser null
    apellido = models.CharField(max_length=100, blank=True, null=True) # Apellido puede ser opcional
    correo = models.EmailField(unique=True, max_length=255) # Usar EmailField para validación
    contrasena = models.CharField(max_length=255)
    # NOTA IMPORTANTE: Para contraseñas, NUNCA las guardes en texto plano.
    # Django tiene un sistema de autenticación robusto. Considera heredar de AbstractUser
    # o usar un OneToOneField a un modelo User de Django para manejar esto de forma segura.
    fecha_nacimiento = models.DateField(blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True) # Mejor usar ImageField
    fecha_registro = models.DateTimeField(auto_now_add=True, blank=True, null=True) # auto_now_add si Django lo gestiona
    ultima_conexion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False # Mantenlo si gestionas la tabla externamente
        db_table = 'usuarios'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip() + f" ({self.correo})"

    # Si usaras el sistema de auth de Django, tendrías métodos como:
    # def set_password(self, raw_password):
    #     self.contrasena = make_password(raw_password)
    #
    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.contrasena)


class Publicaciones(models.Model):
    publicacionid = models.AutoField(primary_key=True)
    # Cambiar 'usuarioid' a 'usuario' para seguir convenciones
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid') # CASCADE es común aquí
    contenido_texto = models.TextField(blank=True, null=True)
    url_media = models.FileField(upload_to='media_publicaciones/', blank=True, null=True) # Mejor FileField o ImageField
    # TIPO_CONTENIDO_CHOICES = [('TEXTO', 'Texto'), ('IMAGEN', 'Imagen'), ('VIDEO', 'Video')]
    # tipo_contenido = models.CharField(max_length=10, choices=TIPO_CONTENIDO_CHOICES, default='TEXTO', blank=True, null=True)
    tipo_contenido = models.CharField(max_length=50, blank=True, null=True) # Ajusta según tu ENUM/necesidad
    fecha_publicacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publicaciones'
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ['-fecha_publicacion'] # Ordenar por más reciente por defecto

    def __str__(self):
        return f"Publicación ({self.publicacionid}) por {self.usuario.nombre}"


class Comentarios(models.Model):
    comentarioid = models.AutoField(primary_key=True)
    # Cambiar nombres de FK
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    contenido_comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comentarios'
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['fecha_comentario']

    def __str__(self):
        return f"Comentario ({self.comentarioid}) de {self.usuario.nombre} en Pub ({self.publicacion.publicacionid})"


class Megusta(models.Model):
    megustaid = models.AutoField(primary_key=True)
    # Cambiar nombres de FK
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    fecha_megusta = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'megusta'
        unique_together = (('usuario', 'publicacion'),) # Ya lo tenías, ¡bien!
        verbose_name = "Me Gusta"
        verbose_name_plural = "Me Gusta"

    def __str__(self):
        return f"{self.usuario.nombre} le gusta Pub ({self.publicacion.publicacionid})"


class Amistades(models.Model):
    amistadid = models.AutoField(primary_key=True)
    # Nombres de campos más descriptivos
    solicitante = models.ForeignKey(Usuarios, models.CASCADE, related_name='amistades_enviadas', db_column='usuario1')
    receptor = models.ForeignKey(Usuarios, models.CASCADE, related_name='amistades_recibidas', db_column='usuario2')

    # ESTADO_AMISTAD_CHOICES = [('PENDIENTE', 'Pendiente'), ('ACEPTADA', 'Aceptada')] # ...etc.
    # estado_amistad = models.CharField(max_length=20, choices=ESTADO_AMISTAD_CHOICES, default='PENDIENTE')
    estado_amistad = models.CharField(max_length=50, blank=True, null=True) # Ajusta
    fecha_solicitud = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_aceptacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'amistades'
        unique_together = (('solicitante', 'receptor'),)
        verbose_name = "Amistad"
        verbose_name_plural = "Amistades"

    def __str__(self):
        return f"Amistad {self.amistadid}: {self.solicitante.nombre} -> {self.receptor.nombre} ({self.estado_amistad})"


class Mensajes(models.Model):
    mensajeid = models.AutoField(primary_key=True)
    emisor = models.ForeignKey(Usuarios, models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(Usuarios, models.CASCADE, related_name='mensajes_recibidos')
    contenido_mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_lectura = models.DateTimeField(blank=True, null=True)
    # ESTADO_MENSAJE_CHOICES = [('ENVIADO', 'Enviado'), ('LEIDO', 'Leído')]
    # estado_mensaje = models.CharField(max_length=10, choices=ESTADO_MENSAJE_CHOICES, default='ENVIADO')
    estado_mensaje = models.CharField(max_length=50, blank=True, null=True) # Ajusta

    class Meta:
        managed = False
        db_table = 'mensajes'
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"Mensaje ({self.mensajeid}) de {self.emisor.nombre} a {self.receptor.nombre}"


class Notificaciones(models.Model):
    notificacionid = models.AutoField(primary_key=True)
    usuario_destino = models.ForeignKey(Usuarios, models.CASCADE)
    # TIPO_NOTIFICACION_CHOICES = [('NUEVO_MEGUSTA', 'Nuevo Me Gusta'), ('NUEVO_COMENTARIO', 'Nuevo Comentario'), ...]
    # tipo_notificacion = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES)
    tipo_notificacion = models.CharField(max_length=100, blank=True, null=True) # Ajusta
    elemento_relacionado_id = models.IntegerField(blank=True, null=True) # Considera GenericForeignKey para flexibilidad
    mensaje_notificacion = models.CharField(max_length=500) # Asumimos que no puede ser null
    leida = models.BooleanField(default=False) # Default a False es común
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notificaciones'
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notif ({self.notificacionid}) para {self.usuario_destino.nombre}: {self.mensaje_notificacion[:50]}"
