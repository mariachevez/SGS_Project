from django.urls import path
from .views import *

urlpatterns = [
    path('', PruebaView.as_view(), name='index')
]