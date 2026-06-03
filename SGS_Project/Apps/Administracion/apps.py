from django.apps import AppConfig
from django.db.models.signals import post_migrate

def crear_usuario_inicial(sender, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        # Verificamos si ya existe el admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='1234'
            )
            print("====================================================")
            print("¡Usuario administrador inicial creado con éxito!") 
            print("====================================================")
    except Exception:
        pass

class AdministracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Apps.Administracion'
    
    def ready(self):
        post_migrate.connect(crear_usuario_inicial, sender=self)

