from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

def index(request):
    return HttpResponsePermanentRedirect("/scoresheet/")
