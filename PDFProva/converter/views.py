# converter/views.py (VERSÃO FINAL E AJUSTADA)

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404, HttpRequest
from django.conf import settings
import os
import time
import json
import fitz  # PyMuPDF
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
from .services.sign_pdf import process_sign_pdf

def clean_old_converted_files():
    """
    Remove arquivos na pasta 'converted' com mais de 30 minutos.
    """
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    if not os.path.exists(converted_dir):
        return
    now = time.time()
    for filename in os.listdir(converted_dir):
        file_path = os.path.join(converted_dir, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > 1800: # 30 minutos
                try:
                    os.remove(file_path)
                except OSError:
                    pass

def index(request):
    return render(request, 'converter/index.html')

def sign_index(request):
    return render(request, 'sign.html')

# --- LÓGICA DE UPLOAD OTIMIZADA ---

def sign_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    # Coleta dos arquivos e dados do formulário
    pdf_file = request.FILES.get('document_file')
    pfx_file = request.FILES.get('certificate_file')
    password = request.POST.get('password')
    signer_email = request.POST.get('signer_email')

    # Validações
    if not pdf_file or not pfx_file:
        return JsonResponse({'success': False, 'message': 'Documento e certificado são obrigatórios.'}, status=400)
    if not password:
        return JsonResponse({'success': False, 'message': 'A senha do certificado é obrigatória.'}, status=400)

    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    base_filename = os.path.splitext(pdf_file.name)[0]

    # Chama o serviço para realizar a assinatura
    success, message, output_filename, _ = process_sign_pdf(
        pdf_file_bytes=pdf_file.read(),
        pfx_file_bytes=pfx_file.read(),
        password=password,
        output_dir=converted_dir,
        base_filename=base_filename,
        signer_email=signer_email
    )

    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/'
    })

def convert_image(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    image_file = request.FILES.get('file')
    if not image_file:
        return JsonResponse({'success': False, 'message': 'Nenhuma imagem enviada.'}, status=400)

    target_format = request.POST.get('target_format')
    if not target_format:
        return JsonResponse({'success': False, 'message': 'Formato de destino não especificado.'}, status=400)

    try:
        rotation_angle = int(request.POST.get('rotation', '0'))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Ângulo de rotação inválido.'}, status=400)

    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    # Chama o serviço
    success, message, output_filename, _ = process_convert_image(
        image_file=image_file,
        target_format=target_format,
        rotation_angle=rotation_angle,
        output_dir=converted_dir
    )

    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/'
    })

def upload_file(request):
    """
    Esta view agora apenas valida o PDF enviado e retorna o número de páginas,
    sem salvar o arquivo no disco.
    """
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        
        try:
            # Lê o arquivo em memória para validação
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            num_pages = doc.page_count
            doc.close()
            return JsonResponse({'success': True, 'filename': uploaded_file.name, 'num_pages': num_pages})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Arquivo PDF inválido ou corrompido: {str(e)}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


# --- VIEWS DAS FERRAMENTAS ---

def image_to_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    image_files = request.FILES.getlist('files')

    if not image_files:
        return JsonResponse({'success': False, 'message': 'Nenhuma imagem enviada.'}, status=400)
    
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    # Chama o serviço
    success, message, output_filename, _ = process_image_to_pdf(
        image_files=image_files,
        output_dir=converted_dir
    )

    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/'
    })

def unlock_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    pdf_file = request.FILES.get('file')
    password = request.POST.get('password')

    if not pdf_file:
        return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    if not password:
        return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
    
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    base_filename = os.path.splitext(pdf_file.name)[0]

    # Chama o serviço para remover a senha
    success, message, output_filename, _ = process_unlock_pdf(
        pdf_file_bytes=pdf_file.read(),
        password=password,
        output_dir=converted_dir,
        base_filename=base_filename
    )

    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/'
    })

def protect_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    pdf_file = request.FILES.get('file')
    password = request.POST.get('password')

    if not pdf_file:
        return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
    if not password:
        return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
    
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    base_filename = os.path.splitext(pdf_file.name)[0]

    success, message, output_filename, _ = process_protect_pdf(
        pdf_file_bytes=pdf_file.read(),
        password=password,
        output_dir=converted_dir,
        base_filename=base_filename
    )

    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/'
    })


def merge_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    pdf_files = request.FILES.getlist('files')
    if len(pdf_files) < 2: return JsonResponse({'success': False, 'message': 'Selecione pelo menos 2 arquivos.'}, status=400)
    
    try: rotations = json.loads(request.POST.get('rotations', '[]'))
    except json.JSONDecodeError: return JsonResponse({'success': False, 'message': 'Dados de rotação inválidos.'}, status=400)

    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    success, message, output_filename = process_merge_pdf(pdf_files, rotations, converted_dir)

    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
        
    return JsonResponse({
        'success': True, 
        'message': message, 
        'download_url': f'/tools/download/converted/{output_filename}/'
    })

def split_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    pdf_file = request.FILES.get('file')
    if not pdf_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        
    try:
        split_mode = request.POST.get('split_mode', 'individual')
        selections = json.loads(request.POST.get('selections', '[]'))
        rotations = json.loads(request.POST.get('rotations', '[]'))
    except json.JSONDecodeError: return JsonResponse({'success': False, 'message': 'Dados de formulário inválidos.'}, status=400)

    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    base_filename = os.path.splitext(pdf_file.name)[0]

    success, message, output_filename = process_split_pdf(
        pdf_file_bytes=pdf_file.read(),
        split_mode=split_mode,
        selections=selections,
        rotations=rotations,
        output_dir=converted_dir,
        base_filename=base_filename
    )

    if not success: return JsonResponse({'success': False, 'message': message}, status=500)

    response_data = {'success': True, 'message': message}
    download_path = f'/tools/download/converted/{output_filename}/'
    if split_mode == 'merge':
        response_data['download_url'] = download_path
    else:
        response_data['download_zip'] = download_path
        
    return JsonResponse(response_data)

def compress_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    pdf_file = request.FILES.get('file')
    if not pdf_file: return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)

    compression_level = request.POST.get('compression_level', 'medium')
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    base_filename = os.path.splitext(pdf_file.name)[0]

    success, message, output_filename, original_size, compressed_size, ratio = process_compress_pdf(
        pdf_file_bytes=pdf_file.read(),
        output_dir=converted_dir,
        base_filename=base_filename,
        compression_level=compression_level
    )

    if not success: return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_url': f'/tools/download/converted/{output_filename}/',
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': ratio
    })

# <<< VIEW AJUSTADA >>>
def pdf_to_word(request):
    clean_old_converted_files()
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        
        converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
        os.makedirs(converted_dir, exist_ok=True)
        
        success, converted_filename, error_message = convert_pdf_to_word(
            uploaded_file, converted_dir
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Conversão para Word realizada!',
                'download_url': f'/tools/download/converted/{converted_filename}/'
            })
        else:
            return JsonResponse({'success': False, 'message': f'Erro ao converter para Word: {error_message}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

# <<< VIEW AJUSTADA >>>
def pdf_to_excel(request):
    clean_old_converted_files()
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        
        converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
        os.makedirs(converted_dir, exist_ok=True)
        
        success, converted_filename, error_message = convert_pdf_to_excel(
            uploaded_file, converted_dir
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Conversão para Excel realizada!',
                'download_url': f'/tools/download/converted/{converted_filename}/'
            })
        else:
            return JsonResponse({'success': False, 'message': f'Erro ao converter para Excel: {error_message}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

# <<< VIEW AJUSTADA >>>
def pdf_to_image(request: HttpRequest) -> JsonResponse:    
    clean_old_converted_files()
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)

    image_format = request.POST.get('image_format', 'png').lower()
    
    try:
        rotations = json.loads(request.POST.get('rotations', '[]'))
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Dados de rotação inválidos.'}, status=400)

    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    success, message, output_filename = convert_pdf_to_images(
        uploaded_file,
        converted_dir,
        image_format,
        rotations
    )
        
    if not success:
        return JsonResponse({'success': False, 'message': message}, status=500)

    return JsonResponse({
        'success': True,
        'message': message,
        'download_zip': f'/tools/download/converted/{output_filename}/'
    })

def download_converted(request, filename):
    clean_old_converted_files()
    file_path = os.path.join(settings.MEDIA_ROOT, 'converted', filename)
    if not os.path.exists(file_path):
        raise Http404("Arquivo não encontrado.")
    
    return FileResponse(open(file_path, 'rb'), as_attachment=True)