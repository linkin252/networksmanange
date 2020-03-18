# Create your views here.
# encoding = utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from . import views
from instruments.models import National

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'National_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return National.objects.order_by('id')

