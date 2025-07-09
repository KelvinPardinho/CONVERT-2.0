# converter/views.py (VERSÃO FINAL COM CORREÇÃO NO SPLIT_PDF)

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404, HttpRequest
from django.conf import settings
from django.urls import reverse
import os
import time
import json
import fitz
from .services.pdf_to_word import convert_pdf_to_word
from .services.pdf_to_excel import convert_pdf_to_excel
from .services.pdf_to_image import convert_pdf_to_images
from .services.split_pdf import process_split_pdf
from .services.merge_pdf import process_merge_pdf
from .services.compress_pdf import process_compress_pdf
from .services.protect_pdf import process_protect_pdf
from .services.unlock_pdf import process_unlock_pdf
from .services.image_to_pdf import process_image_to_pdf
from .services.convert_image import process_convert_image

def clean_old_converted_files():
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    if not os.path.exists(converted_dir): return
    now = time.time()
    for filename in os.listdir(converted_dir):
        file_path = os.path.join(converted_dir, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > 1800:
                try: os.remove(file_path)
                except OSError: pass

def get_converted_dir():
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    return converted_dir

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'converter/index.html')

def sign_index(request):
    return render(request, 'sign.html')

def upload_file(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            num_pages = doc.page_count
            doc.close()
            return JsonResponse({'success': True, 'filename': uploaded_file.name, 'num_pages': num_pages})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Arquivo PDF inválido ou corrompido: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


# --- VIEWS DAS FERRAMENTAS ---
def sign_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    try:
        pdf_file = request.FILES.get('document_file')
        pfx_file = request.FILES.get('certificate_file')
        password = request.POST.get('password')

        if not all([pdf_file, pfx_file, password]):
            return JsonResponse({'success': False, 'message': 'Documento, certificado e senha são obrigatórios.'}, status=400)

        # Coleta os dados de posicionamento da assinatura do POST
        signature_data = {
            'pageIndex': int(request.POST.get('page_index', 0)),
            'x1': int(request.POST.get('x1', 50)),
            'y1': int(request.POST.get('y1', 50)),
            'x2': int(request.POST.get('x2', 300)),
            'y2': int(request.POST.get('y2', 150)),
        }
        
        converted_dir = get_converted_dir() # Reutiliza sua função auxiliar
        base_filename = os.path.splitext(pdf_file.name)[0]

        # Chama o novo serviço de assinatura
        success, message, output_filename, _ = process_sign_pdf(
            pdf_bytes=pdf_file.read(),
            pfx_bytes=pfx_file.read(),
            password=password,
            signature_data=signature_data,
            output_dir=converted_dir,
            base_filename=base_filename
        )

        if not success:
            return JsonResponse({'success': False, 'message': message}, status=500)

        # Gera a URL de download correta
        download_url = reverse('converter:download_converted', args=[output_filename])

        return JsonResponse({
            'success': True,
            'message': message,
            'download_url': download_url
        })

    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Dados de posicionamento inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro inesperado: {str(e)}'}, status=500)
    
def convert_image(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    image_file = request.FILES.get('file')
    if not image_file: return JsonResponse({'success': False, 'message': 'Nenhuma imagem enviada.'}, status=400)
    target_format = request.POST.get('target_format')
    if not target_format: return JsonResponse({'success': False, 'message': 'Formato de destino não especificado.'}, status=400)
    try: rotation_angle = int(request.POST.get('rotation', '0'))
    except ValueError: return JsonResponse({'success': False, 'message': 'Ângulo de rotação inválido.'}, status=400)

    success, message, output_filename, _ = process_convert_image(image_file, target_format, rotation_angle, get_converted_dir())
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def image_to_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    image_files = request.FILES.getlist('files')
    if not image_files: return JsonResponse({'success': False, 'message': 'Nenhuma imagem enviada.'}, status=400)
    success, message, output_filename, _ = process_image_to_pdf(image_files, get_converted_dir())
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def unlock_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    pdf_file = request.FILES.get('file')
    password = request.POST.get('password')
    if not pdf_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    if not password: return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
    base_filename = os.path.splitext(pdf_file.name)[0]
    success, message, output_filename, _ = process_unlock_pdf(pdf_file.read(), password, get_converted_dir(), base_filename)
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def protect_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    pdf_file = request.FILES.get('file')
    password = request.POST.get('password')
    if not pdf_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    if not password: return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
    base_filename = os.path.splitext(pdf_file.name)[0]
    success, message, output_filename, _ = process_protect_pdf(pdf_file.read(), password, get_converted_dir(), base_filename)
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def merge_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    pdf_files = request.FILES.getlist('files')
    if len(pdf_files) < 2: return JsonResponse({'success': False, 'message': 'Selecione pelo menos 2 arquivos.'}, status=400)
    try: rotations = json.loads(request.POST.get('rotations', '[]'))
    except json.JSONDecodeError: return JsonResponse({'success': False, 'message': 'Dados de rotação inválidos.'}, status=400)
    success, message, output_filename = process_merge_pdf(pdf_files, rotations, get_converted_dir())
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def split_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    try:
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
            
        split_mode = request.POST.get('split_mode', 'individual')
        selections = json.loads(request.POST.get('selections', '[]'))
        rotations = json.loads(request.POST.get('rotations', '[]'))

        # Verificação explícita no backend
        if (split_mode == 'individual' or split_mode == 'merge') and not any(selections):
             return JsonResponse({'success': False, 'message': 'Nenhuma página foi selecionada.'}, status=400)

        base_filename = os.path.splitext(pdf_file.name)[0]

        # <<< A CORREÇÃO ESTÁ AQUI >>>
        # Lemos o conteúdo do arquivo em bytes e o passamos para a função de serviço.
        # Isso garante que a função `process_split_pdf` receba o tipo de dado correto.
        success, message, output_filename, _ = process_split_pdf(
            pdf_file_bytes=pdf_file.read(),
            split_mode=split_mode,
            selections=selections,
            rotations=rotations,
            output_dir=get_converted_dir(),
            base_filename=base_filename
        )

        if not success:
            return JsonResponse({'success': False, 'message': message}, status=400)

        response_data = {'success': True, 'message': message}
        download_url = reverse('converter:download_converted', args=[output_filename])
        if '.zip' in output_filename:
            response_data['download_zip'] = download_url
        else:
            response_data['download_url'] = download_url
            
        return JsonResponse(response_data)
        
    except Exception as e:
        # Captura qualquer outra exceção e retorna um JSON de erro
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro interno no servidor: {str(e)}'}, status=500)

def compress_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    pdf_file = request.FILES.get('file')
    if not pdf_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    compression_level = request.POST.get('compression_level', 'medium')
    base_filename = os.path.splitext(pdf_file.name)[0]
    success, message, output_filename, original_size, compressed_size, ratio = process_compress_pdf(pdf_file.read(), get_converted_dir(), base_filename, compression_level)
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename]), 'original_size': original_size, 'compressed_size': compressed_size, 'compression_ratio': ratio})

def pdf_to_word(request):
    clean_old_converted_files()
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        success, converted_filename, error_message = convert_pdf_to_word(uploaded_file, get_converted_dir())
        if success:
            return JsonResponse({'success': True, 'message': 'Conversão para Word realizada!', 'download_url': reverse('converter:download_converted', args=[converted_filename])})
        else:
            return JsonResponse({'success': False, 'message': f'Erro ao converter para Word: {error_message}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def pdf_to_excel(request):
    clean_old_converted_files()
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        success, converted_filename, error_message = convert_pdf_to_excel(uploaded_file, get_converted_dir())
        if success:
            return JsonResponse({'success': True, 'message': 'Conversão para Excel realizada!', 'download_url': reverse('converter:download_converted', args=[converted_filename])})
        else:
            return JsonResponse({'success': False, 'message': f'Erro ao converter para Excel: {error_message}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def pdf_to_image(request: HttpRequest) -> JsonResponse:    
    clean_old_converted_files()
    if request.method != "POST": return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)
    uploaded_file = request.FILES.get('file')
    if not uploaded_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    image_format = request.POST.get('image_format', 'png').lower()
    try: rotations = json.loads(request.POST.get('rotations', '[]'))
    except json.JSONDecodeError: return JsonResponse({'success': False, 'message': 'Dados de rotação inválidos.'}, status=400)
    success, message, output_filename = convert_pdf_to_images(uploaded_file, get_converted_dir(), image_format, rotations)
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_zip': reverse('converter:download_converted', args=[output_filename])})

def download_converted(request, filename):
    file_path = os.path.join(get_converted_dir(), filename)
    if not os.path.exists(file_path):
        raise Http404("Arquivo não encontrado. Pode ter expirado.")
    return FileResponse(open(file_path, 'rb'), as_attachment=True)