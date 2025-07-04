from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [

    path('', views.home, name='home'),
    path('ferramentas/', views.index, name='converter_index'),
    path('assinar/', views.sign_index, name='sign_index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('merge/', views.merge_pdf, name='merge_pdf'),
    path('split/', views.split_pdf, name='split_pdf'),
    path('compress/', views.compress_pdf, name='compress_pdf'),
    path('protect/', views.protect_pdf, name='protect_pdf'),
    path('unlock/', views.unlock_pdf, name='unlock_pdf'),
    path('image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    path('convert-image/', views.convert_image, name='convert_image'),
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('pdf-to-excel/', views.pdf_to_excel, name='pdf_to_excel'),
    path('pdf-to-image/', views.pdf_to_image, name='pdf_to_image'),
    
    path('download/converted/<str:filename>/', views.download_converted, name='download_converted'),
]