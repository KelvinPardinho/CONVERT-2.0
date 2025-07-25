from django.shortcuts import render
import os
from django.http import HttpResponse
from django.conf import settings

def home(request):
    return render(request, 'index.html')

def ads_txt_view(request):
    ads_path = os.path.join(settings.BASE_DIR, 'ads.txt')
    with open(ads_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/plain')