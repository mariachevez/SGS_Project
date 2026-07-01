from django.db import models
from core.models import *
# Create your models here.



class Persona(ModeloBase):
    nombres = models.CharField(default='', max_length=100, verbose_name=u'Nombres')
    apellido1 = models.CharField(default='', max_length=50, verbose_name=u"1er Apellido")
    apellido2 = models.CharField(default='', max_length=50, verbose_name=u"2do Apellido")
    identificacion = models.CharField(default='', max_length=20, verbose_name=u"Identificación", blank=True, db_index=True)
    nacimiento = models.DateField(verbose_name=u"Fecha de nacimiento o constitución")
    sexo = models.CharField(max_length=1, choices=CoreChoices.Sexo.choices, default=CoreChoices.Sexo.MASCULINO, verbose_name='Sexo')    
    pais = models.ForeignKey(Pais, blank=True, null=True, related_name='mis_personas', verbose_name=u'País residencia', on_delete=models.CASCADE)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, related_name='mis_personas', verbose_name=u"Provincia de residencia", on_delete=models.CASCADE)
    canton = models.ForeignKey(Canton, blank=True, null=True, related_name='mis_personas', verbose_name=u"Canton de residencia", on_delete=models.CASCADE)
    telefono = models.CharField(default='', max_length=50, verbose_name=u"Telefono movil")
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electronico personal")
    usuario = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    foto = models.FileField(upload_to='foto_persona/', blank=True, null=True, verbose_name='Foto de la persona.')
    def __str__(self):
        return u'%s %s %s' % (self.apellido1, self.apellido2, self.nombres)

    class Meta:
        verbose_name = u"Persona"
        verbose_name_plural = u"Personal"
        ordering = ['apellido1', 'apellido2', 'nombres']
        
    def nombre_minus(self):
        try:
            nombreslist = self.nombres.split(' ')
            nombrepersona = self.nombres.capitalize()
            if len(nombreslist) == 2:
                nombrepersona = '{} {}'.format(str(nombreslist[0]).capitalize(), str(nombreslist[1]).capitalize())
                return u'%s' % (nombrepersona)
            elif len(nombreslist) == 3:
                nombrepersona = '{} {} {}'.format(str(nombreslist[0]).capitalize(), str(nombreslist[1]).capitalize(),
                                                  str(nombreslist[2]).capitalize())
                return u'%s' % (nombrepersona)
            else:
                return u'%s' % (nombrepersona)
        except Exception as ex:
            return self.nombres.capitalize()
        
    def primerNombre(self):
        if self.nombres:
            return self.nombres.split()[0]
        else:
            return ''

    def nombre_completo_minus(self):
        apellido1list = self.apellido1.split(' ')
        apellido1 = self.apellido1.capitalize()
        if len(apellido1list) == 2:
            apellido1 = '{} {}'.format(str(apellido1list[0]).capitalize(), str(apellido1list[1]).capitalize())
        elif len(apellido1list) == 3:
            apellido1 = '{} {} {}'.format(str(apellido1list[0]).capitalize(), str(apellido1list[1]).capitalize(),
                                          str(apellido1list[2]).capitalize())
        apellido2list = self.apellido2.split(' ')
        apellido2 = self.apellido2.capitalize()
        if len(apellido2list) == 2:
            apellido2 = '{} {}'.format(str(apellido2list[0]).capitalize(), str(apellido2list[1]).capitalize())
        elif len(apellido2list) == 3:
            apellido2 = '{} {} {}'.format(str(apellido2list[0]).capitalize(), str(apellido2list[1]).capitalize(),
                                          str(apellido2list[2]).capitalize())
        completo = '{} {} {}'.format(str(self.nombre_minus()), str(apellido1), str(apellido2))
        return u'%s' % (completo)

    def get_foto(self):
        try:
            if self.foto:
                return self.foto.url
            else:
                if self.sexo:
                    if self.sexo == 'M':
                        return '/static/img/icono-hombre.svg'
                    else:
                        return '/static/img/icono-mujer.svg'
        except Exception:
            return '/static/img/icono-hombre.svg'


class Area(ModeloBase):
    director = models.ForeignKey(Persona, verbose_name='Director del Área', blank=True, 
                                 null=True, related_name='areas_dirigidas', on_delete=models.CASCADE)
    nombre = models.TextField(verbose_name='Nombre del Área', blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    
    
    def __str__(self):
        return f'Area: {self.nombre}'
        #return f'Director: {self.director.nombre_completo_minus()} - {self.nombre}'

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nombre']

class AreaPersona(ModeloBase):
    area = models.ForeignKey(Area, verbose_name='Área', blank=True, null=True, related_name='trabajadores', on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, verbose_name='Persona', blank=True, null=True, related_name='areas_trabajo', on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.area
    
    class Meta:
        verbose_name = 'Área de persona'
        verbose_name_plural = 'Áreas de la persona'
        ordering = ['-id']

class Grupo(ModeloBase):
    nombre = models.TextField(verbose_name='Nombre del Grupo', blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['nombre']
        
class GrupoPersona(ModeloBase):
    grupo = models.ForeignKey(Grupo, verbose_name='Grupo', blank=True, null=True, related_name='integrantes', on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, verbose_name='Persona', blank=True, null=True, related_name='mis_grupos', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.grupo
    
    class Meta:
        verbose_name = 'Grupo de Persona'
        verbose_name_plural = 'Grupos de Persona'
        ordering = ['-id']

class ModuloCategorias(ModeloBase):
    nombre = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Nombre')
    prioridad = models.IntegerField(null=True, blank=True)

    def mismodulos(self, mismodulos):
        return self.modulo_set.values('id', 'icono', 'nombre','descripcion', 'url').filter(status=True, id__in=mismodulos.values_list('id',flat=True))

    def __str__(self):
        return '{} {}'.format(self.nombre, self.prioridad)

    class Meta:
        verbose_name = 'Categorias de Módulos'
        verbose_name_plural = 'Categorias de Módulos'
        ordering = ('prioridad', 'nombre')

class GrupoCategoria(ModeloBase):
    grupo = models.ForeignKey(Grupo, verbose_name='Grupo', related_name='grupo_categorias', blank=True, null=True)
    categoria = models.ForeignKey(ModuloCategorias, verbose_name='Categoria', related_name='grupo_categorias', blank=True, null=True)

    def __str__(self):
        return f'{self.grupo.nombre} - {self.categoria.nombre}'
    
class Modulo(ModeloBase):
    url = models.CharField(blank=True, null=True, max_length=100, verbose_name='URL')
    nombre = models.CharField(blank=True, null=True, max_length=100, verbose_name='Nombre')
    icono = models.CharField(blank=True, null=True, max_length=100, verbose_name='Icono')
    descripcion = models.CharField(blank=True, null=True, max_length=200, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    categorias = models.ManyToManyField(ModuloCategorias, verbose_name='Categorias')
    submodulo = models.BooleanField(default=False, verbose_name=u'¿Es submódulo?')

    
    def __str__(self):
        return u'%s (/%s)' % (self.nombre, self.url)
    
    class Meta:
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"
        ordering = ['nombre']
        unique_together = ('url',)

class ModuloGrupo(ModeloBase):
    nombre = models.CharField(blank=True, null=True, max_length=100, verbose_name=' Nombre')
    descripcion = models.CharField(blank=True, null=True, max_length=200, verbose_name='Descripción')
    modulos = models.ManyToManyField(Modulo, verbose_name='Modulos')
    grupos = models.ManyToManyField(Grupo, verbose_name='Grupos')
    prioridad = models.IntegerField(default=0, verbose_name='Prioridad')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = 'Grupo de modulos'
        verbose_name_plural = "Grupos de modulos"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def modulos_activos(self):
        return self.modulos.filter(activo=True)

    def modulos_activos(self):
        return self.modulos.filter(activo=True)

    def modules(self):
        return self.modulos.all()