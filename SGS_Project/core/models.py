from django.db import models
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import *
from datetime import timedelta, date, time, datetime
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from SGS_Project.settings import ADMINISTRADOR__ID
from django.db.models import TextChoices

# Create your models here.

class CoreChoices:

    class Sexo(TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"
    
    class TipoNotificacion(TextChoices):
        ALTA = "A", "Alta"
        MEDIA = "M", 'Media'
        BAJA = "B", 'Baja'

    class EstadoSolicitud(TextChoices):
        PENDIENTE = "P", "Pendiente"
        RECHAZADO = "R", "Rechazado"
        APROBADO = "A", "Aprobado"
    
    class EstadoBiometrico(TextChoices):
        APROBADO = "A", "Aprobado"
        RECHAZADO = "R", "Rechazado"
    
    class TipoSolicitud(TextChoices):
        EQUIPO_TRABAJO = "E", "Equipo de Trabajo"
        SOPORTE_TECNICO = "S", "Soporte Técnico"


class ModeloBase(models.Model):
    fecha_creacion = models.DateTimeField(verbose_name='Fecha de creacion', blank=True, null=True)
    fecha_modificacion = models.DateTimeField(verbose_name='Fecha de modificacion', blank=True, null=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', verbose_name='Usuario de creacion', blank=True, null=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+',verbose_name='Usuario de modificacion', blank=True, null=True)
    status = models.BooleanField(verbose_name='Estado del registro', default=True)

    def delete_status(self):
        self.status = False
        self.save()

    def save(self, *args, **kwargs):
        usuario = None
        fecha_modificacion = datetime.now()
        fecha_creacion = None
        update_fields = None
        if len(args):
            usuario = args[0].user.id
        for key, value in kwargs.items():
            if 'usuario_id' == key:
                usuario = value
            if 'fecha_modificacion' == key:
                fecha_modificacion = value
            if 'fecha_creacion' == key:
                fecha_creacion = value
            if 'update_fields' == key:
                update_fields = value
        if self.id:
            self.usuario_modificacion_id = usuario if usuario else ADMINISTRADOR__ID
            self.fecha_modificacion = fecha_modificacion
            if update_fields is not None:
                update_fields = [*update_fields, 'usuario_modificacion_id', 'fecha_modificacion']
                kwargs['update_fields'] = list(set(update_fields))
        else:
            self.usuario_creacion_id = usuario if usuario else ADMINISTRADOR__ID
            self.fecha_creacion = fecha_modificacion
            if fecha_creacion:
                self.fecha_creacion = fecha_creacion
        models.Model.save(self, update_fields=update_fields)

    class Meta:
        abstract = True

class EliminarBase(View):
    model = None

    def post(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk, status=True)
        messages.success(request, 'Registro eliminado con éxito')
        obj.delete_status()
        return JsonResponse({
            'success': True,
            'message': 'Registro eliminado correctamente'
        })


class Pais(ModeloBase):
    nombre = models.TextField(verbose_name='Pais', blank=True, null=True)
    prefijo = models.TextField(verbose_name='Prefijo del pais', blank=True, null=True)
    
    def __str__(self):
        return self.nombre or ""
    
    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().upper()

        if self.prefijo:
            self.prefijo = self.prefijo.strip().upper()
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Pais"
        verbose_name_plural = "Paises"
        ordering = ['nombre']

    
class Provincia(ModeloBase):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='mis_provincias', null=True, blank=True, verbose_name='Pais')
    nombre = models.TextField(verbose_name='Provincia', blank=True, null=True)
    
    def __str__(self):
        return self.nombre or ""
    
    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ['pais__nombre', 'nombre']

class Canton(ModeloBase):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='mis_cantones', null=True, blank=True, verbose_name='Provincia')
    nombre = models.TextField(verbose_name='Canton', blank=True, null=True)
    
    def __str__(self):
        return self.nombre or ""
    
    class Meta:
        verbose_name = u"Canton"
        verbose_name_plural = u"Cantones"
        ordering = ['provincia__pais__nombre', 'provincia__nombre', 'nombre']

