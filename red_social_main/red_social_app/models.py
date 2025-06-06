from django.db import models

class Usuarios(models.Model):
    usuarioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    correo = models.CharField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255, db_column='contraseña')  # ¡OJO! La columna real es 'contraseña'
    fecha_nacimiento = models.DateField(blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.CharField(max_length=512, blank=True, null=True)
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
    tipo_contenido = models.CharField(max_length=50, blank=True, null=True)  # tipo_contenido_tipo_contenido_enum
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


class Comentarios(models.Model):
    comentarioid = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    contenido_comentario = models.TextField()
    fecha_comentario = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

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
    usuario = models.ForeignKey(Usuarios, models.CASCADE, db_column='usuarioid')
    publicacion = models.ForeignKey(Publicaciones, models.CASCADE, db_column='publicacionid')
    fecha_megusta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'megusta'
        unique_together = (('usuario', 'publicacion'),)
        verbose_name = "Me Gusta"
        verbose_name_plural = "Me Gusta"

    def __str__(self):
        return f"{self.usuario.nombre} le gusta Pub ({self.publicacion.publicacionid})"


class Amistades(models.Model):
    amistadid = models.AutoField(primary_key=True)
    usuario1_id = models.IntegerField(db_column='usuario1')
    usuario2_id = models.IntegerField(db_column='usuario2')
    estado_amistad = models.CharField(max_length=50, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(blank=True, null=True)
    fecha_aceptacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'amistades'
        unique_together = (('usuario1_id', 'usuario2_id'),)
        verbose_name = "Amistad"
        verbose_name_plural = "Amistades"

    def __str__(self):
        return f"Amistad {self.amistadid}: {self.usuario1_id} -> {self.usuario2_id} ({self.estado_amistad})"


class Mensajes(models.Model):
    mensajeid = models.AutoField(primary_key=True)
    emisor_id = models.IntegerField(db_column='emisor_id')
    receptor_id = models.IntegerField(db_column='receptor_id')
    contenido_mensaje = models.TextField()
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_lectura = models.DateTimeField(blank=True, null=True)
    estado_mensaje = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mensajes'
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"Mensaje ({self.mensajeid}) de {self.emisor_id} a {self.receptor_id}"


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
        return f"Notif ({self.notificacionid}) para {self.usuario_destino_id}: {self.mensaje_notificacion[:50]}"