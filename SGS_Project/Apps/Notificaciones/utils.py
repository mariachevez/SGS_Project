import mimetypes
import os
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Notificaciones
from core.models import CoreChoices

def generar_notificacion(titulo, descripcion, destinatario, tipo_notificacion=CoreChoices.TipoNotificacion.ALTA, url=None):
    eNoti = Notificaciones()
    eNoti.titulo = titulo
    eNoti.descripcion = descripcion
    eNoti.tipo_notificacion = tipo_notificacion
    eNoti.destinatario = destinatario
    eNoti.url = url
    eNoti.save()


mimetypes.add_type('image/avif', '.avif')
mimetypes.add_type('image/webp', '.webp')
def enviar_correo_html(
        asunto,
        plantilla_html,
        contexto,
        destinatarios,
        copias=None,
        adjuntos=None,
        imagenes_incrustadas=None
):
    """
    Función genérica para enviar correos electrónicos en Django.

    :param asunto: str -> Asunto del correo.
    :param plantilla_html: str -> Ruta de la plantilla HTML (ej. 'emails/alerta_biometrico.html').
    :param contexto: dict -> Variables que se renderizarán en la plantilla HTML.
    :param destinatarios: list o str -> Correo(s) del destinatario principal.
    :param copias: list o str (opcional) -> Correo(s) para enviar con copia (CC).
    :param adjuntos: list de rutas de archivos (opcional) -> Rutas físicas de archivos para adjuntar.
    :param imagenes_incrustadas: dict (opcional) -> Diccionario con formato { 'id_imagen': 'ruta_fisica_imagen' }
                                  para incrustar fotos directamente en el HTML usando <img src="cid:id_imagen">.
    """
    # 1. Normalizar destinatarios y copias para que siempre sean listas
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]

    lista_cc = []
    if copias:
        if isinstance(copias, str):
            lista_cc = [copias]
        else:
            lista_cc = list(copias)

    # 2. Renderizar el contenido HTML con las variables del contexto
    html_content = render_to_string(plantilla_html, contexto)
    text_content = strip_tags(html_content)

    # 3. Configurar el correo base
    correo_remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'mchevezv@unemi.edu.ec')

    msg = EmailMultiAlternatives(
        subject=asunto,
        body=text_content,
        from_email=correo_remitente,
        to=destinatarios,
        cc=lista_cc
    )
    msg.attach_alternative(html_content, "text/html")

    # 4. Adjuntar archivos de manera genérica (Documentos, PDFs, etc.)
    if adjuntos:
        for ruta_archivo in adjuntos:
            if os.path.exists(ruta_archivo):
                msg.attach_file(ruta_archivo)
            else:
                print(f"Advertencia de Correo: El archivo adjunto no existe en la ruta {ruta_archivo}")

    # 5. Incrustar imágenes dentro del cuerpo HTML (Fotos del Biométrico) con detección segura de subtipo
    if imagenes_incrustadas:
        msg.mixed_subtype = 'related'
        for cid, ruta_imagen in imagenes_incrustadas.items():
            if os.path.exists(ruta_imagen):

                # 1. Intentamos deducir el tipo usando mimetypes (ahora reconocerá .avif)
                mime_type, _ = mimetypes.guess_type(ruta_imagen)
                subtipo = None

                if mime_type and mime_type.startswith('image/'):
                    subtipo = mime_type.split('/')[-1]  # Ej: 'avif', 'png', 'jpeg'
                else:
                    # 2. Respaldo manual estricto analizando la extensión del archivo
                    nombre_archivo_baja = ruta_imagen.lower()
                    if nombre_archivo_baja.endswith('.avif'):
                        subtipo = 'avif'
                    elif nombre_archivo_baja.endswith('.webp'):
                        subtipo = 'webp'
                    elif nombre_archivo_baja.endswith('.png'):
                        subtipo = 'png'
                    elif nombre_archivo_baja.endswith('.jpg') or nombre_archivo_baja.endswith('.jpeg'):
                        subtipo = 'jpeg'
                    else:
                        subtipo = 'png'  # Por defecto si todo lo demás falla

                with open(ruta_imagen, 'rb') as img_file:
                    # Inyectamos el subtipo garantizado (ej. _subtype='avif')
                    mime_image = MIMEImage(img_file.read(), _subtype=subtipo)

                    mime_image.add_header('Content-ID', f'<{cid}>')
                    mime_image.add_header('Content-Disposition', 'inline', filename=os.path.basename(ruta_imagen))
                    msg.attach(mime_image)
            else:
                print(f"Advertencia de Correo: La imagen a incrustar no existe en la ruta {ruta_imagen}")

    # 6. Enviar el correo
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error crítico al enviar correo electrónico: {e}")
        return False