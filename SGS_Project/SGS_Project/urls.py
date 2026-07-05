"""
URL configuration for SGS_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from SGS_Project.views import PanelPrincipal

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_not_required(auth_views.LoginView.as_view()), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', PanelPrincipal.as_view(), name='panel_principal'),
    path('', include('Apps.Administracion.urls')),
    path('', include('Apps.Solicitudes.urls')),
    path('', include('Apps.Notificaciones.urls')),

    path('password_reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='registration/password_reset_form.html',
         # ESTA LÍNEA ES LA MAGIA: Le dice a Django que envíe el correo usando HTML
         html_email_template_name='registration/password_reset_email.html',
         extra_context={'domain': '127.0.0.1:8000', 'protocol': 'http'}), name='password_reset'),    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
