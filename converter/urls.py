from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [

    path('', views.home, name='home'),
    path('ferramentas/', views.index, name='converter_index'),
    path('assinar/', views.sign_index, name='sign_index'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/merge/', views.merge_pdf, name='merge_pdf'),
    path('api/split/', views.split_pdf, name='split_pdf'),
    path('api/compress/', views.compress_pdf, name='compress_pdf'),
    path('api/protect/', views.protect_pdf, name='protect_pdf'),
    path('api/unlock/', views.unlock_pdf, name='unlock_pdf'),
    path('api/image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    path('api/convert-image/', views.convert_image, name='convert_image'),
    path('api/pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('api/pdf-to-excel/', views.pdf_to_excel, name='pdf_to_excel'),
    path('api/pdf-to-image/', views.pdf_to_image, name='pdf_to_image'),
    
    path('download/converted/<str:filename>/', views.download_converted, name='download_converted'),
]