from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    # Paginas
    path('', views.home, name='home'),
    path('ferramentas/', views.index, name='converter_index'),
    path('assinar/', views.sign_index, name='sign_index'),
    path('pdf-para-word/', views.pdf_para_word_page, name='pdf_para_word_page'),
    path('pdf-para-excel/', views.pdf_para_excel_page, name='pdf_para_excel_page'),
    path('unir_pdf/', views.unir_pdf_page, name='unir_pdf_page'),
    path('dividir_pdf/', views.dividir_pdf_page, name='dividir_pdf_page'),
    path('comprimir_pdf/', views.comprimir_pdf_page, name='comprimir_pdf_page'),
    path('proteger_pdf/', views.proteger_pdf_page, name='proteger_pdf_page'),
    path('remover_senha_pdf/', views.remover_senha_pdf_page, name='remover_senha_pdf_page'),
    path('pdf_para_imagem/', views.pdf_para_imagem_page, name='pdf_para_imagem_page'),
    path('imagem_para_pdf/', views.imagem_para_pdf_page, name='imagem_para_pdf_page'),
    path('converte_imagem/', views.converte_imagem_page, name='converte_imagem_page'),
    path('rotacionar_pdf/', views.rotacionar_pdf_page, name='rotacionar_pdf_page'),
    path('numerar_pagina/', views.numerar_pagina_page, name='numerar_pagina_page'),
    path('word_para_pdf/', views.word_para_pdf_page, name='word_para_pdf_page'),
    path('exce_para_pdf/', views.excel_para_pdf_page, name='excel_para_pdf_page'),

    # API Endpoints
    path('api/sign_pdf', views.sign_pdf, name='sign_pdf'),
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
    path('api/rotention-pdf/', views.rodar_pdf, name='rotention_pdf'),
    path('api/number-page/', views.number_page, name='number_page'),
    path('api/word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
    path('api/excel-to-pdf/', views.excel_to_pdf, name='excel_to_pdf'),
    
    path('download/converted/<str:filename>/', views.download_converted, name='download_converted'),
]