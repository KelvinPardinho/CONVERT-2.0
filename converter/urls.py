from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [

    path('', views.home, name='home'),
    path('ferramentas/', views.index, name='converter_index'),
    path('assinar/', views.sign_index, name='sign_index'),
    path('tools/upload/', views.upload_file, name='upload_file'),
    path('tools/merge/', views.merge_pdf, name='merge_pdf'),
    path('tools/split/', views.split_pdf, name='split_pdf'),
    path('tools/compress/', views.compress_pdf, name='compress_pdf'),
    path('tools/protect/', views.protect_pdf, name='protect_pdf'),
    path('tools/unlock/', views.unlock_pdf, name='unlock_pdf'),
    path('tools/image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    path('tools/convert-image/', views.convert_image, name='convert_image'),
    path('tools/pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('tools/pdf-to-excel/', views.pdf_to_excel, name='pdf_to_excel'),
    path('tools/pdf-to-image/', views.pdf_to_image, name='pdf_to_image'),
    
    path('tools/download/converted/<str:filename>/', views.download_converted, name='download_converted'),
]