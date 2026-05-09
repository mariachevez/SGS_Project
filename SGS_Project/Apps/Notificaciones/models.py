from django.db import models
from core.models import *
from Apps.Administracion.models import *
# Create your models here.

class Notificaciones(ModeloBase):
    destinatario = models.ForeignKey(Persona, verbose_name='Destinatario', blank=True, null=True, related_name='persona', on_delete=models.CASCADE)
    titulo = models.TextField(verbose_name='Título de la notificación', blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripción de la notificación', blank=True, null=True)
    estado_notificacion = models.BooleanField(verbose_name='Notificación revisada', default=False)
    tipo_notificacion = models.CharField(verbose_name='Prioridad de la Notificación', max_length=1, 
                                         choices=CoreChoices.TipoNotificacion.choices, 
                                         default=CoreChoices.TipoNotificacion.BAJA)
    
    
    def _str_(self):
        return f'{self.titulo} - {self.descripcion}'
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-id']
