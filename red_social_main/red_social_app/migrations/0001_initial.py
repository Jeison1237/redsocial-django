# Generated by Django 5.2.1 on 2025-05-28 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Amistades',
            fields=[
                ('amistadid', models.AutoField(primary_key=True, serialize=False)),
                ('estado_amistad', models.CharField(blank=True, max_length=50, null=True)),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_aceptacion', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Amistad',
                'verbose_name_plural': 'Amistades',
                'db_table': 'amistades',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Comentarios',
            fields=[
                ('comentarioid', models.AutoField(primary_key=True, serialize=False)),
                ('contenido_comentario', models.TextField()),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Comentario',
                'verbose_name_plural': 'Comentarios',
                'db_table': 'comentarios',
                'ordering': ['fecha_comentario'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Megusta',
            fields=[
                ('megustaid', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_megusta', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Me Gusta',
                'verbose_name_plural': 'Me Gusta',
                'db_table': 'megusta',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Mensajes',
            fields=[
                ('mensajeid', models.AutoField(primary_key=True, serialize=False)),
                ('contenido_mensaje', models.TextField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_lectura', models.DateTimeField(blank=True, null=True)),
                ('estado_mensaje', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Mensaje',
                'verbose_name_plural': 'Mensajes',
                'db_table': 'mensajes',
                'ordering': ['-fecha_envio'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Notificaciones',
            fields=[
                ('notificacionid', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_notificacion', models.CharField(blank=True, max_length=100, null=True)),
                ('elemento_relacionado_id', models.IntegerField(blank=True, null=True)),
                ('mensaje_notificacion', models.CharField(max_length=500)),
                ('leida', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'db_table': 'notificaciones',
                'ordering': ['-fecha_creacion'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Publicaciones',
            fields=[
                ('publicacionid', models.AutoField(primary_key=True, serialize=False)),
                ('contenido_texto', models.TextField(blank=True, null=True)),
                ('url_media', models.FileField(blank=True, null=True, upload_to='media_publicaciones/')),
                ('tipo_contenido', models.CharField(blank=True, max_length=50, null=True)),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Publicación',
                'verbose_name_plural': 'Publicaciones',
                'db_table': 'publicaciones',
                'ordering': ['-fecha_publicacion'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('usuarioid', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(blank=True, max_length=100, null=True)),
                ('correo', models.EmailField(max_length=255, unique=True)),
                ('contrasena', models.CharField(max_length=255)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('ubicacion', models.CharField(blank=True, max_length=255, null=True)),
                ('foto_perfil', models.ImageField(blank=True, null=True, upload_to='fotos_perfil/')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, null=True)),
                ('ultima_conexion', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'db_table': 'usuarios',
                'managed': False,
            },
        ),
    ]
