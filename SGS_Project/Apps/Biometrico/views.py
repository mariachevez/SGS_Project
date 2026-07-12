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
from core.views import AjaxExceptionMixin
from .models import Configuracion, CabRegistro, DetRegistro
from .forms import ConfiguracionForm
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView, EntidadesSesionMixin
from ..Administracion.models import AreaPersona

# --- CARGA GLOBAL DEL MODELO YOLO ---
from pathlib import Path

RUTAS_MODELOS = {
    "modelo1": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models" / "best.pt",
        "conf": 0.85
    },
    "modelo2": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models_2" / "best.pt",
        "conf": 0.35
    },
    "modelo3": {
        "ruta": settings.BASE_DIR / "Apps" / "Biometrico" / "ia_models_3" / "best.pt",
        "conf": 0.50
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
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            nombre_archivo = f"biometrico_{persona.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            archivo_foto = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

            cabecera = CabRegistro.objects.create(
                persona=persona,
                area_id=area_id,
                tipo=tipo_registro,
                estado='R'
            )

            # Inicializamos todos los campos requeridos del detalle en False
            detalle = DetRegistro.objects.create(
                cabecera=cabecera,
                foto=archivo_foto,
                casco=False,
                guantes=False,
                mandil=False
            )

            ruta_fisica_foto = detalle.foto.path
            resultados_ia = self.evaluar_epp_ia(ruta_fisica_foto)

            detalle.casco = resultados_ia['casco']
            detalle.guantes = resultados_ia['guantes']
            detalle.mandil = resultados_ia['mandil']

            # Lógica de aprobación basada en el casco obligatorio
            if detalle.casco:
                cabecera.estado = 'A'
                mensaje = "Acceso Autorizado. Uso de casco verificado correctamente."
            else:
                cabecera.estado = 'R'
                mensaje = "Acceso Denegado. No se detectó el casco de seguridad obligatorio."

            cabecera.save()
            detalle.save()

            # --- SÓLO AQUÍ SE AGREGA EL LOG DE AUDITORÍA TRANSACCIONAL ---
            log(
                mensaje=f"Marcaje registrado por {self.nombre_en_sesion}. Área: {cabecera.area.nombre}. EPI detectados -> Casco: {detalle.casco}, Guantes: {detalle.guantes}, Mandil: {detalle.mandil}. Resultado: {cabecera.get_estado_display()}",
                request=self.request,
                accion="add",
                objeto=cabecera
            )

            # --- FIX DE FECHA NAIVE ---
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

    def evaluar_epp_ia(self, ruta_imagen):
        """
        Escanea la imagen utilizando cada modelo para su propósito específico:
        - Modelo 1: Casco (conf: 0.85)
        - Modelo 2: Guantes (conf: 0.50)
        - Modelo 3: Mandil (conf: 0.15)
        """
        epp = {'casco': False, 'guantes': False, 'mandil': False}

        if not MODELOS_YOLO:
            print("Error: No existen modelos YOLO cargados.")
            return epp

        try:
            # --- EVALUAR MODELO 1: CASCO ---
            if "modelo1" in MODELOS_YOLO:
                config1 = MODELOS_YOLO["modelo1"]
                resultados1 = config1["modelo"](ruta_imagen, conf=config1["conf"])
                nombres_clases1 = resultados1[0].names

                for caja in resultados1[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases1[clase_id].lower()
                    # Solo buscamos cascos en este modelo
                    if nombre_clase in ['helmet', 'hard-hat', 'casco']:
                        epp['casco'] = True
                        break  # Si ya encontramos uno, podemos pasar al siguiente modelo

            # --- EVALUAR MODELO 2: GUANTES ---
            if "modelo2" in MODELOS_YOLO:
                config2 = MODELOS_YOLO["modelo2"]
                resultados2 = config2["modelo"](ruta_imagen, conf=config2["conf"])
                nombres_clases2 = resultados2[0].names

                for caja in resultados2[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases2[clase_id].lower()
                    # Solo buscamos guantes en este modelo
                    if nombre_clase in ['gloves', 'guantes', 'glove', 'heat_glove']:
                        epp['guantes'] = True
                        break

            # --- EVALUAR MODELO 3: MANDIL ---
            if "modelo3" in MODELOS_YOLO:
                config3 = MODELOS_YOLO["modelo3"]
                resultados3 = config3["modelo"](ruta_imagen, conf=config3["conf"])
                nombres_clases3 = resultados3[0].names

                for caja in resultados3[0].boxes:
                    clase_id = int(caja.cls[0].item())
                    nombre_clase = nombres_clases3[clase_id].lower()
                    # Solo buscamos mandiles en este modelo
                    if nombre_clase in ['vest', 'apron', 'mandil', 'protective-clothing', 'welding_apron',
                                        'welding_suit', 'wearing-apron']:
                        epp['mandil'] = True
                        break

            return epp

        except Exception as e:
            print(f"Error crítico procesando la IA por separado: {e}")
            return epp

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