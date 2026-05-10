from django.shortcuts import render
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView


class PruebaView(TemplateView):
    template_name = 'index.html'
        