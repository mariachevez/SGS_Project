from django.db import models
from core.models import *
from Apps.Administracion.models import *

# Create your models here.

class Solicitudes(ModeloBase):
    persona = models.ForeignKey(Persona, verbose_name='Solicitante', blank=True, null=True, related_name='solicitudes', on_delete=models.CASCADE)
    area = models.ForeignKey(Area, verbose_name='Área', blank=True, null=True, related_name='solicitudes', on_delete=models.CASCADE)
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    estado_solicitud = models.CharField(verbose_name='Estado de la Solicitud', choices=CoreChoices.EstadoSolicitud.choices, 
                                        default=CoreChoices.EstadoSolicitud.PENDIENTE)
    fecha_resolucion = models.DateTimeField(verbose_name='Fecha de Resolución', blank=True, null=True)
    tipo_solicitud = models.CharField(verbose_name='Tipo de Solicitud', choices=CoreChoices.TipoSolicitud.choices, blank=True, null=True)
    
    def __str(self):
        return f'Solicitante: {self.persona.nombre_completo_minus()}, {self.descripcion}'
    
    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering = ['-id']