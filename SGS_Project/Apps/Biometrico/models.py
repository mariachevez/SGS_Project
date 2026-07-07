from django.db import models
from core.models import *
from Apps.Administracion.models import *
# Create your models here.

class Configuracion(ModeloBase):
    area = models.ForeignKey(Area, verbose_name='Configuración Marcaje para Área', related_name='configuracion', on_delete=models.CASCADE, blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    activo = models.BooleanField(verbose_name='Activo para marcaje', default=True)
    
    def ___str___(self):
        return f'{self.descripcion}'
    
    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        ordering = ['-id']

class CabRegistro(ModeloBase):
    persona = models.ForeignKey(Persona, verbose_name='Persona', blank=True, null=True, related_name='registros_biometricos', on_delete=models.CASCADE)
    area = models.ForeignKey(Area, verbose_name='Área', blank=True, null=True, related_name='registros_biometricos', on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, verbose_name='Estado del registro',
                              choices=CoreChoices.EstadoBiometrico.choices, blank=True, null=True)
    tipo = models.CharField(max_length=1, verbose_name='Tipo de registro', choices=CoreChoices.TipoRegistroBiometrico.choices, blank=True, null=True)

    def ___str___(self):
        return f'{self.persona.nombre_completo_minus()} - {self.area.nombre} - {self.estado}'
    
    class Meta:
        verbose_name = 'Cabecera Biométrico'
        verbose_name_plural = 'Cabeceras Biométrico'
        ordering = ['-id']

class DetRegistro(ModeloBase):
    cabecera = models.ForeignKey(CabRegistro, verbose_name='Cabecera', blank=True, null=True, related_name='detalles', on_delete=models.CASCADE)
    casco = models.BooleanField(verbose_name='Tiene casco', blank=True, null=True, default=False)
    guantes = models.BooleanField(verbose_name='Tiene guantes de seguridad', blank=True, null=True, default=False)
    mandil = models.BooleanField(verbose_name='Tiene mandil de seguridad', blank=True, null=True, default=False)
    foto = models.FileField(verbose_name='Foto del Biométrico', blank=True, null=True, upload_to='fotos_biometrico/')

    def ___str___(self):
        return f'{self.cabecera.persona.nombre_completo_minus()} - Casco: {self.casco}, Guantes: {self.guantes}, Mandil: {self.mandil}'
    
    class Meta:
        verbose_name = 'Detalle Registro'
        verbose_name_plural = 'Detalles Registro'
        ordering = ['-id']