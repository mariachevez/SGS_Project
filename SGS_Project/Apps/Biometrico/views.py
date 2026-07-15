import io
from PIL import Image
import os
from django.conf import settings
from ultralytics import YOLO
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from core.funciones import log
from core.models import CoreChoices
from core.views import AjaxExceptionMixin
from .models import Configuracion, CabRegistro, DetRegistro
from .forms import ConfiguracionForm
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView, EntidadesSesionMixin
from ..Administracion.models import AreaPersona

# --- CARGA GLOBAL DEL MODELO YOLO ---
from pathlib import Path

from ..Notificaciones.utils import generar_notificacion, enviar_correo_html

RUTAS_MODELOS = {
    "modelo1": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models" / "best.pt",
        "conf": 0.85
    },
    "modelo2": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models_2" / "best.pt",
        "conf": 0.45
    },
    "modelo3": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models_3" / "best.pt",
        "conf": 0.55
    },
}

MODELOS_YOLO = {}
for nombre, config in RUTAS_MODELOS.items():
    try:
        MODELOS_YOLO[nombre] = {
            "modelo": YOLO(config["ruta"]),
            "conf": config["conf"]
        }
    except Exception as e:
        print(f"No se pudo cargar {nombre}: {e}")


class ListarConfiguracionesBiometrico(ListView):
    model = Configuracion
    template_name = 'configuracion_index.html'
    paginate_by = 10
    context_object_name = 'configuraciones'

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True)
        search = self.request.GET.get('s')
        estado = self.request.GET.get('estado')

        if search:
            queryset = queryset.filter(area__nombre__icontains=search)

        if estado in ['true', 'false']:
            val_bool = estado == 'true'
            queryset = queryset.filter(activo=val_bool)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de configuraciones de acceso a las áreas'
        context['url_formcrear'] = reverse_lazy('crear_configuracion')
        context['titulo'] = 'Registrar Configuración'
        context['estado'] = self.request.GET.get('estado', '')
        return context


class CrearConfiguracionView(BaseCreateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listar_configuraciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_configuracion')
        return context


class EditarConfiguracionView(BaseUpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listar_configuraciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_configuracion', kwargs={'pk': self.object.pk})
        return context


class EliminarConfiguracionView(AjaxExceptionMixin, EntidadesSesionMixin, View):
    model = Configuracion
    redirect_url = reverse_lazy('listar_configuraciones')

    def post(self, request, *args, **kwargs):
        objeto = get_object_or_404(self.model, pk=self.kwargs.get('pk'))

        try:
            estado_actual = objeto.activo
            objeto.activo = not estado_actual
            objeto.save()

            nombre_objeto = self.model._meta.verbose_name.capitalize()
            accion_str = "activado" if objeto.activo else "inactivado"
            mensaje = f"Registro de {nombre_objeto} {accion_str} exitosamente."

            log(
                mensaje=f"{self.nombre_en_sesion} Cambió el estado de marcaje a {'ACTIVO' if objeto.activo else 'INACTIVO'} del registro: {str(objeto)}",
                request=self.request,
                accion="edit" if objeto.activo else "del",
                objeto=objeto
            )
            messages.success(request, mensaje)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'result': True,
                    'message': mensaje,
                    'url': self.get_redirect_url()
                })

        except Exception as e:
            mensaje_error = f"Error al cambiar el estado: {str(e)}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'result': False, 'message': mensaje_error}, status=500)
            messages.error(request, mensaje_error)

        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        if not self.redirect_url:
            raise ValueError(f"{self.__class__.__name__} debe definir 'redirect_url'.")
        return str(self.redirect_url)


class ModuloMarcajeView(EntidadesSesionMixin, TemplateView):
    template_name = 'ingreso_area.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        persona = self.persona_sesion

        tiene_acceso = False
        mensaje_bloqueo = ""

        if not persona:
            mensaje_bloqueo = "No se ha detectado un perfil de trabajador asociado a su cuenta."
        else:
            areas_persona = AreaPersona.objects.filter(persona=persona, status=True)

            if not areas_persona.exists():
                mensaje_bloqueo = "No se encuentra configurado en ningún área de ingreso. Por favor, comuníquese con el director de su área."
            else:
                areas_ids = areas_persona.values_list('area_id', flat=True)
                configuracion = Configuracion.objects.filter(area_id__in=areas_ids, activo=True, status=True).first()

                if not configuracion:
                    mensaje_bloqueo = "Su área asignada no tiene una configuración de marcaje activa en este momento. Por favor, comuníquese con el director de su área."
                else:
                    tiene_acceso = True
                    context['configuracion'] = configuracion
                    context['area'] = configuracion.area

                    context['ultimos_movimientos'] = CabRegistro.objects.filter(
                        persona=persona,
                        area=configuracion.area
                    ).order_by('-id')[:5]

        context['tiene_acceso'] = tiene_acceso
        context['mensaje_bloqueo'] = mensaje_bloqueo

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        context['ip_detectada'] = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get(
            'REMOTE_ADDR')
        return context


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ProcesarMarcajeView(EntidadesSesionMixin, View):

    def post(self, request, *args, **kwargs):
        persona = self.persona_sesion
        if not persona:
            return JsonResponse({'result': False, 'message': 'Sesión inválida.'}, status=403)

        base64_data = request.POST.get('imagen')
        tipo_registro = request.POST.get('tipo')
        area_id = request.POST.get('area_id')

        if not base64_data or not tipo_registro or not area_id:
            return JsonResponse({'result': False, 'message': 'Faltan parámetros obligatorios.'}, status=400)

        try:
            # 1. Obtener la configuración de marcaje activa del área solicitada
            configuracion = Configuracion.objects.filter(
                area_id=area_id,
                activo=True,
                status=True
            ).first()

            if not configuracion:
                return JsonResponse({
                    'result': False,
                    'message': 'No existe una configuración de marcaje activa para esta área.'
                }, status=400)

            # 2. Procesar y guardar la imagen enviada
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            nombre_archivo = f"biometrico_{persona.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            archivo_foto = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

            # Crear cabecera (inicia como rechazada por seguridad hasta evaluar)
            cabecera = CabRegistro.objects.create(
                persona=persona,
                area_id=area_id,
                tipo=tipo_registro,
                estado='R'
            )

            # Crear detalle del registro asignándole la foto
            detalle = DetRegistro.objects.create(
                cabecera=cabecera,
                foto=archivo_foto,
                casco=False,
                guantes=False,
                mandil=False
            )

            # 3. Evaluar la imagen con los modelos de Inteligencia Artificial
            ruta_fisica_foto = detalle.foto.path
            resultados_ia = self.evaluar_epi_ia(ruta_fisica_foto)

            # Almacenar en base de datos lo que la IA efectivamente detectó
            detalle.casco = resultados_ia['casco']
            detalle.guantes = resultados_ia['guantes']
            detalle.mandil = resultados_ia['mandil']
            detalle.save()

            # 4. Validar dinámicamente EPIs requeridos vs EPIs detectados
            obligatorios_faltantes = []
            alertas_no_obligatorias = []

            # Validación de Casco
            if configuracion.casco:
                if not detalle.casco:
                    obligatorios_faltantes.append("Casco de seguridad")
            else:
                if not detalle.casco:
                    alertas_no_obligatorias.append("Casco de seguridad (No requerido)")

            # Validación de Guantes
            if configuracion.guantes:
                if not detalle.guantes:
                    obligatorios_faltantes.append("Guantes protectores")
            else:
                if not detalle.guantes:
                    alertas_no_obligatorias.append("Guantes protectores (No requeridos)")

            # Validación de Mandil
            if configuracion.mandil:
                if not detalle.mandil:
                    obligatorios_faltantes.append("Mandil de protección")
            else:
                if not detalle.mandil:
                    alertas_no_obligatorias.append("Mandil de protección (No requerido)")

            # 5. Determinar el estado final de la transacción de acceso
            # Si hay algún EPI obligatorio que no fue detectado, se RECHAZA
            if obligatorios_faltantes:
                cabecera.estado = 'R'
                mensaje = f"Acceso Denegado. No se detectaron los siguientes EPI obligatorios: {', '.join(obligatorios_faltantes)}."
            else:
                cabecera.estado = 'A'
                mensaje = "Acceso Autorizado. Se validaron correctamente todos los EPI requeridos."

            cabecera.save()

            # --- DETECCIÓN DE 3 RECHAZOS EN EL DÍA POR TIPO (INGRESO / SALIDA) ---
            if cabecera.estado == 'R':
                ahora = timezone.now()
                if timezone.is_aware(ahora):
                    hoy_local = timezone.localtime(ahora)
                else:
                    hoy_local = ahora

                inicio_dia = hoy_local.replace(hour=0, minute=0, second=0, microsecond=0)
                fin_dia = hoy_local.replace(hour=23, minute=59, second=59, microsecond=999999)

                tipo_normalizado = tipo_registro.upper()
                if tipo_normalizado in ['INGRESO', 'I']:
                    valor_tipo_db = "I"  # CoreChoices.TipoRegistroBiometrico.INGRESO
                elif tipo_normalizado in ['SALIDA', 'S']:
                    valor_tipo_db = "S"  # CoreChoices.TipoRegistroBiometrico.SALIDA
                else:
                    valor_tipo_db = tipo_registro

                # Contar cuántos rechazos lleva este usuario hoy en este tipo específico de registro (I o S)
                cantidad_rechazos = CabRegistro.objects.filter(
                    persona=persona,
                    tipo=valor_tipo_db,
                    estado='R',
                    fecha_creacion__range=(inicio_dia, fin_dia)
                ).count()

                if cantidad_rechazos >= 3:
                    generar_notificacion(
                        titulo='Alerta de Seguridad',
                        descripcion=f'{persona} acumuló {cantidad_rechazos} rechazos de tipo {cabecera.get_tipo_display()} hoy.',
                        tipo_notificacion=CoreChoices.TipoNotificacion.BAJA,
                        destinatario=cabecera.area.director,
                        url=f'/mi_area'
                    )
                    destinatarios = [cabecera.area.director.email]
                    copias_cc = [persona.email]

                    # 2. Configurar las variables que se mostrarán en la plantilla del correo
                    contexto_email = {
                        'nombre_trabajador': persona,
                        'identificacion': persona.identificacion,
                        'area': cabecera.area.nombre,
                        'tipo_movimiento': cabecera.get_tipo_display(),
                        'intentos_fallidos': cantidad_rechazos,
                        'faltantes': ", ".join(obligatorios_faltantes),
                        'fecha_alerta': hoy_local.strftime('%d/%m/%Y a las %H:%M %p')
                    }

                    # 3. Si existe una foto en el detalle, la incrustamos directamente en el cuerpo del correo
                    imagenes_a_incrustar = {}
                    if detalle.foto and os.path.exists(detalle.foto.path):
                        imagenes_a_incrustar['foto_epi'] = detalle.foto.path

                    # 4. Enviar el correo
                    enviar_correo_html(
                        asunto=f"ALERTA DE SEGURIDAD: Intentos de Acceso Fallidos - {persona}",
                        plantilla_html='alerta_biometrico.html',
                        contexto=contexto_email,
                        destinatarios=destinatarios,
                        copias=copias_cc,
                        imagenes_incrustadas=imagenes_a_incrustar
                    )

                    tipo_movimiento_str = cabecera.get_tipo_display()
                    print(
                        f"ALERTA CRÍTICA: {persona} acumuló {cantidad_rechazos} rechazos de tipo {tipo_movimiento_str} hoy.")
                    pass

            log(
                mensaje=(
                    f"Marcaje de ingreso registrado por {self.nombre_en_sesion}. Área: {cabecera.area.nombre}. "
                    f"EPI Detectados -> Casco: {detalle.casco}, Guantes: {detalle.guantes}, Mandil: {detalle.mandil}. "
                    f"Configuración Requerida -> Casco: {configuracion.casco}, Guantes: {configuracion.guantes}, Mandil: {configuracion.mandil}. "
                    f"Resultado final: {cabecera.get_estado_display()}"
                ),
                request=self.request,
                accion="add",
                objeto=cabecera
            )

            fecha_creacion = cabecera.fecha_creacion
            if timezone.is_aware(fecha_creacion):
                fecha_creacion = timezone.localtime(fecha_creacion)

            fecha_str = fecha_creacion.strftime('%d/%m/%Y, %H:%M %p')

            return JsonResponse({
                'result': True,
                'estado': cabecera.estado,
                'mensaje': mensaje,
                'movimiento': {
                    'tipo': cabecera.get_tipo_display().upper(),
                    'fecha': fecha_str,
                }
            })

        except Exception as e:
            return JsonResponse({'result': False, 'message': f'Error en el procesamiento: {str(e)}'}, status=500)

    def evaluar_epi_ia(self, ruta_imagen):
        """
        Evalúa individualmente cada modelo YOLO y devuelve un diccionario con
        la detección (True/False) de cada EPI.
        """
        epi = {'casco': False, 'guantes': False, 'mandil': False}

        if not MODELOS_YOLO:
            print("Error: No existen modelos YOLO cargados.")
            return epi

        try:
            # --- EVALUAR MODELO 1: CASCO ---
            if "modelo1" in MODELOS_YOLO:
                config1 = MODELOS_YOLO["modelo1"]
                resultados1 = config1["modelo"](ruta_imagen, conf=config1["conf"])
                nombres_clases1 = resultados1[0].names

                for caja in resultados1[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases1[clase_id].lower()
                    if nombre_clase in ['helmet', 'hard-hat', 'casco']:
                        epi['casco'] = True
                        break

            # --- EVALUAR MODELO 2: GUANTES ---
            if "modelo2" in MODELOS_YOLO:
                config2 = MODELOS_YOLO["modelo2"]
                resultados2 = config2["modelo"](ruta_imagen, conf=config2["conf"])
                nombres_clases2 = resultados2[0].names

                for caja in resultados2[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases2[clase_id].lower()
                    if nombre_clase in ['gloves', 'guantes', 'glove', 'heat_glove']:
                        epi['guantes'] = True
                        break

            # --- EVALUAR MODELO 3: MANDIL ---
            if "modelo3" in MODELOS_YOLO:
                config3 = MODELOS_YOLO["modelo3"]
                resultados3 = config3["modelo"](ruta_imagen, conf=config3["conf"])
                nombres_clases3 = resultados3[0].names

                for caja in resultados3[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases3[clase_id].lower()
                    if nombre_clase in ['vest', 'apron', 'mandil', 'protective-clothing', 'welding_apron',
                                        'welding_suit', 'wearing-apron']:
                        epi['mandil'] = True
                        break

            return epi

        except Exception as e:
            print(f"Error crítico procesando la IA por separado: {e}")
            return epi

@method_decorator(csrf_exempt, name='dispatch')
class DetectarCoordenadasView(View):
    def post(self, request, *args, **kwargs):
        if not MODELOS_YOLO:
            return JsonResponse({'result': False, 'message': 'Modelo IA no disponible.'}, status=500)

        base64_data = request.POST.get('imagen')
        if not base64_data:
            return JsonResponse({'result': False, 'message': 'No se envió imagen.'}, status=400)

        try:
            format, imgstr = base64_data.split(';base64,')
            image_bytes = base64.b64decode(imgstr)
            imagen = Image.open(io.BytesIO(image_bytes))

            detecciones = []
            for config in MODELOS_YOLO.values():
                modelo = config["modelo"]
                conf = config["conf"]
                resultados = modelo(imagen, conf=conf)
                cajas = resultados[0].boxes
                nombres = resultados[0].names

                for caja in cajas:
                    x1, y1, x2, y2 = caja.xyxy[0].tolist()
                    confianza = float(caja.conf[0].item())
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres[clase_id]

                    detecciones.append({
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'clase': nombre_clase,
                        'confianza': confianza
                    })

            return JsonResponse({
                'result': True,
                'detecciones': detecciones
            })

        except Exception as e:
            print(f"Error en detección en tiempo real: {e}")
            return JsonResponse({'result': False, 'message': str(e)}, status=500)