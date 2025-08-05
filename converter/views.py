from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404, HttpRequest
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_POST
from PyPDF2 import PdfReader, PdfWriter
import os
import time
import json
import fitz
import io
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
from .services.rotention_pdf import process_rotate_pdf
from .services.number_page import process_add_page_numbers
from .services.word_to_pdf import process_word_to_pdf
from .services.excel_to_pdf import process_excel_to_pdf

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
@require_POST # Garante que esta view só pode ser acessada via POST
def sign_pdf(request):
    # A verificação 'if request.method != 'POST' não é mais necessária
    clean_old_converted_files()

    try:
        pdf_file = request.FILES.get('document_file')
        pfx_file = request.FILES.get('certificate_file')
        password = request.POST.get('password')

        if not all([pdf_file, pfx_file, password]):
            return JsonResponse({'success': False, 'message': 'Documento, certificado e senha são obrigatórios.'}, status=400)

        signature_data = {
            'pageIndex': int(request.POST.get('page_index', 0)),
            'x1': int(request.POST.get('x1', 50)),
            'y1': int(request.POST.get('y1', 50)),
            'x2': int(request.POST.get('x2', 300)),
            'y2': int(request.POST.get('y2', 150)),
        }
        
        converted_dir = get_converted_dir()
        base_filename = os.path.splitext(pdf_file.name)[0]

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

        download_url = reverse('converter:download_converted', args=[output_filename])

        return JsonResponse({
            'success': True,
            'message': message,
            'download_url': download_url
        })

    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Dados de posicionamento inválidos.'}, status=400)
    except Exception as e:
        print(f"Erro inesperado na view sign_pdf: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro inesperado no servidor.'}, status=500)
    
def convert_image(request):
    """
    Esta view agora lida com dois casos:
    1. GET: Mostra a página HTML inicial para o utilizador carregar uma imagem.
    2. POST: Recebe a imagem, formato e rotação via API (fetch), processa-a e devolve JSON.
    """
    
    # --- CASO 1: O utilizador está a aceder à página pela primeira vez ---
    if request.method == 'GET':
        # Altere 'converter/converte_imagem.html' para o caminho correto do seu template
        return render(request, 'converter/converte_imagem.html')

    # --- CASO 2: O JavaScript está a enviar os dados para serem processados ---
    if request.method == 'POST':
        clean_old_converted_files()
        
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

        try:
            # A sua lógica de processamento, que está correta
            success, message, output_filename, _ = process_convert_image(
                image_file, 
                target_format, 
                rotation_angle, 
                get_converted_dir()
            )
            
            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)
                
            # Resposta JSON de sucesso, agora incluindo o 'file_name'
            return JsonResponse({
                'success': True, 
                'message': message, 
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename # Adicionado para o atributo 'download' no frontend
            })

        except Exception as e:
            # Captura qualquer outro erro inesperado durante o processamento
            return JsonResponse({'success': False, 'message': f"Ocorreu um erro inesperado: {str(e)}"}, status=500)

    # Se o método não for GET nem POST, é inválido
    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

def image_to_pdf(request):
    clean_old_converted_files()
    if request.method != 'POST': return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    image_files = request.FILES.getlist('files')
    if not image_files: return JsonResponse({'success': False, 'message': 'Nenhuma imagem enviada.'}, status=400)
    success, message, output_filename, _ = process_image_to_pdf(image_files, get_converted_dir())
    if not success: return JsonResponse({'success': False, 'message': message}, status=500)
    return JsonResponse({'success': True, 'message': message, 'download_url': reverse('converter:download_converted', args=[output_filename])})

def unlock_pdf(request):
    # --- CASO 1: O utilizador está a aceder à página pela primeira vez ---
    if request.method == 'GET':
        # Altere 'converter/remover_senha.html' para o caminho correto do seu template
        return render(request, 'converter/remover_senha.html')

    # --- CASO 2: O JavaScript está a enviar os dados para serem processados ---
    if request.method == 'POST':
        clean_old_converted_files()
        
        pdf_file = request.FILES.get('file')
        password = request.POST.get('password')
        
        if not pdf_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        if not password:
            return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
 
        try:
            base_filename = os.path.splitext(pdf_file.name)[0]
            success, message, output_filename, _ = process_unlock_pdf(
                pdf_file.read(), 
                password, 
                get_converted_dir(), 
                base_filename
            )
            
            if not success:
                return JsonResponse({'success': False, 'message': message}, status=400)
                
            return JsonResponse({
                'success': True, 
                'message': message, 
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename 
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Ocorreu um erro inesperado: {str(e)}"}, status=500)

    # Se o método não for GET nem POST, é inválido
    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

def protect_pdf(request):
 
    # --- CASO 1: O utilizador está a aceder à página pela primeira vez ---
    if request.method == 'GET':
        # Altere 'converter/proteger_pdf.html' para o caminho correto do seu template
        return render(request, 'converter/proteger_pdf.html')

    # --- CASO 2: O JavaScript está a enviar os dados para serem processados ---
    if request.method == 'POST':
        clean_old_converted_files()
        
        pdf_file = request.FILES.get('file')
        password = request.POST.get('password')
        
        if not pdf_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
        if not password:
            return JsonResponse({'success': False, 'message': 'Nenhuma senha fornecida.'}, status=400)
            
        try:
            base_filename = os.path.splitext(pdf_file.name)[0]
            
            # A sua lógica de processamento, que está correta
            success, message, output_filename, _ = process_protect_pdf(
                pdf_file.read(), 
                password, 
                get_converted_dir(), 
                base_filename
            )
            
            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)
                
            # Resposta JSON de sucesso, agora incluindo o 'file_name'
            return JsonResponse({
                'success': True, 
                'message': message, 
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename # Adicionado para o atributo 'download' no frontend
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Ocorreu um erro inesperado: {str(e)}"}, status=500)

    # Se o método não for GET nem POST, é inválido
    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

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
    """
    Processa a requisição para dividir um arquivo PDF.
    Recebe o arquivo, o modo de divisão, as páginas selecionadas e as rotações.
    """
    # Limpa arquivos antigos para gerenciamento de espaço
    clean_old_converted_files()

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    try:
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)
            
        # Obtém os dados do formulário
        split_mode = request.POST.get('split_mode', 'individual')
        
        # Carrega os dados JSON enviados pelo JavaScript
        selections = json.loads(request.POST.get('selections', '[]'))
        rotations = json.loads(request.POST.get('rotations', '[]'))

        # Validação de segurança no backend
        if split_mode != 'pairs' and not any(selections):
            return JsonResponse({'success': False, 'message': 'Nenhuma página foi selecionada.'}, status=400)

        # Prepara os dados para a função de serviço
        base_filename = os.path.splitext(pdf_file.name)[0]
        pdf_file_bytes = pdf_file.read()

        # Chama a função de serviço que contém a lógica principal
        success, message, output_filename, _ = process_split_pdf(
            pdf_file_bytes=pdf_file_bytes,
            split_mode=split_mode,
            selections=selections,
            rotations=rotations,
            output_dir=get_converted_dir(),
            base_filename=base_filename
        )

        if not success:
            return JsonResponse({'success': False, 'message': message}, status=400)

        # Prepara uma resposta JSON de sucesso consistente
        response_data = {
            'success': True, 
            'message': message,
            'download_url': reverse('converter:download_converted', args=[output_filename]),
            'file_name': output_filename # Importante para o atributo 'download' no HTML
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        # Em produção, é ideal logar o erro para depuração
        # import logging
        # logging.getLogger(__name__).error(f"Erro em split_pdf: {e}")
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro interno no servidor.'}, status=500)

def compress_pdf(request): # ou comprimir_pdf_api
    clean_old_converted_files()
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
    
    pdf_file = request.FILES.get('file')
    if not pdf_file:
        return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'}, status=400)

    try:
        # 1. Obter os dados do formulário
        compression_level = request.POST.get('compression_level', 'medium')
        rotation_angle = int(request.POST.get('rotation', 0)) # Converte para inteiro, padrão 0

        pdf_data = pdf_file.read()

        # 2. Rodar o PDF em memória se o ângulo for maior que 0
        if rotation_angle > 0:
            reader = PdfReader(io.BytesIO(pdf_data))
            writer = PdfWriter()

            for page in reader.pages:
                # O método rotate() adiciona à rotação existente, por isso usamos o ângulo diretamente
                page.rotate(rotation_angle)
                writer.add_page(page)

            # Salva o PDF rodado num objeto de bytes em memória
            rotated_pdf_stream = io.BytesIO()
            writer.write(rotated_pdf_stream)
            rotated_pdf_stream.seek(0)
            
            # Usa os dados do PDF rodado para a compressão
            pdf_data_to_compress = rotated_pdf_stream.read()
        else:
            # Se não houver rotação, usa os dados originais
            pdf_data_to_compress = pdf_data

        # 3. Chamar a função de compressão com os dados corretos
        base_filename = os.path.splitext(pdf_file.name)[0]
        success, message, output_filename, original_size, compressed_size, ratio = process_compress_pdf(
            pdf_data_to_compress, 
            get_converted_dir(), 
            base_filename, 
            compression_level
        )

        if not success:
            return JsonResponse({'success': False, 'message': message}, status=500)
        
        return JsonResponse({
            'success': True, 
            'message': message, 
            'download_url': reverse('converter:download_converted', args=[output_filename]),
            'file_name': output_filename, # Adicionado para o atributo download
            'original_size': original_size, 
            'compressed_size': compressed_size, 
            'compression_ratio': ratio
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro inesperado: {str(e)}'}, status=500)

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

def rodar_pdf(request):
    if request.method == 'GET':
        return render(request, 'converter/rotacionar_pdf.html')
    
    if request.method == 'POST':
        try:
            pdf_file = request.FILES.get('file')
            rotations = json.loads(request.POST.get('rotations', '[]'))

            if not pdf_file:
                return JsonResponse({'success': False, 'message': 'Nenhum ficheiro enviado.'}, status=400)

            success, message, output_filename = process_rotate_pdf(
                pdf_file.read(), 
                rotations,
                pdf_file.name # Passa o nome original aqui
            )

            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)

            return JsonResponse({
                'success': True,
                'message': 'PDF rodado com sucesso!',
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        
def number_page(request):
    if request.method == 'GET':
        return render(request, 'converter/numerar_pagina.html')
    
    if request.method == 'POST':
        clean_old_converted_files()
        try:
            pdf_file = request.FILES.get('file')
            position = request.POST.get('position', 'bottom-center')
            start_from = int(request.POST.get('start_from', 1))
            rotation = int(request.POST.get('rotation', 0)) # Recebe a rotação

            if not pdf_file:
                return JsonResponse({'success': False, 'message': 'Nenhum ficheiro enviado.'}, status=400)

            success, message, output_filename = process_add_page_numbers(
                pdf_file.read(), 
                position, 
                start_from,
                rotation, # Passa a rotação para o service
                get_converted_dir(),
                pdf_file.name
            )

            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)

            return JsonResponse({
                'success': True,
                'message': 'Números de página adicionados com sucesso!',
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

def word_to_pdf(request):
    """
    Lida com o upload e conversão de um ficheiro Word (.doc, .docx) para PDF.
    GET: Mostra a página de upload.
    POST: Processa o ficheiro e devolve uma resposta JSON.
    """
    # Se for um pedido GET, simplesmente renderiza a página HTML
    if request.method == 'GET':
        return render(request, 'converter/word_para_pdf.html') # Confirme o caminho do seu template

    # Se for um pedido POST (da nossa chamada fetch), processa os dados
    if request.method == 'POST':
        clean_old_converted_files()
        
        word_file = request.FILES.get('file')
        if not word_file:
            return JsonResponse({'success': False, 'message': 'Nenhum ficheiro enviado.'}, status=400)
            
        try:
            # Chama a função de serviço para fazer o trabalho pesado
            success, message, output_filename = process_word_to_pdf(word_file, get_converted_dir())
            
            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)
                
            # Resposta JSON de sucesso
            return JsonResponse({
                'success': True, 
                'message': message, 
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Ocorreu um erro inesperado: {str(e)}"}, status=500)

    # Se o método não for GET nem POST, é inválido
    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

def excel_to_pdf(request):
    if request.method == 'GET':
        return render(request, 'converter/excel_para_pdf.html') # Confirme o caminho do seu template

    if request.method == 'POST':
        clean_old_converted_files()
        
        excel_file = request.FILES.get('file')
        if not excel_file:
            return JsonResponse({'success': False, 'message': 'Nenhum ficheiro enviado.'}, status=400)
            
        try:
            success, message, output_filename = process_excel_to_pdf(excel_file, get_converted_dir())
            
            if not success:
                return JsonResponse({'success': False, 'message': message}, status=500)
                
            return JsonResponse({
                'success': True, 
                'message': message, 
                'download_url': reverse('converter:download_converted', args=[output_filename]),
                'file_name': output_filename
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Ocorreu um erro inesperado: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)        

def download_converted(request, filename):
    file_path = os.path.join(get_converted_dir(), filename)
    if not os.path.exists(file_path):
        raise Http404("Arquivo não encontrado. Pode ter expirado.")
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

def pdf_para_word_page(request):
    return render(request, 'converter/pdf_para_word.html')

def unir_pdf_page(request):
    return render(request, 'converter/unir_pdf.html')

def dividir_pdf_page(request):
    return render(request, 'converter/dividir_pdf.html')

def comprimir_pdf_page(request):
    return render(request, 'converter/comprimir_pdf.html')

def proteger_pdf_page(request):
    return render(request, 'converter/proteger_pdf.html')

def remover_senha_pdf_page(request):
    return render(request, 'converter/remover_senha_pdf.html')

def pdf_para_excel_page(request):
    return render(request, 'converter/pdf_para_excel.html')

def pdf_para_imagem_page(request):
    return render(request, 'converter/pdf_para_imagem.html')

def imagem_para_pdf_page(request):
    return render(request, 'converter/imagem_para_pdf.html')

def converte_imagem_page(request):
    return render(request, 'converter/converte_imagem.html')

def rotacionar_pdf_page(request):
    return render(request, 'converter/rotacionar_pdf.html')

def numerar_pagina_page(request):
    return render(request, 'converter/numerar_pagina.html')

def word_para_pdf_page(request):
    return render(request, 'converter/word_para_pdf.html')

def excel_para_pdf_page(request):
    return render(request, 'converter/excel_para_pdf.html')
