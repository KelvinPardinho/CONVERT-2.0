
import os
import uuid
from typing import Tuple, Optional
from datetime import datetime

from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata, PdfSigner
from pyhanko.sign.general import SigningError

# Pillow ainda é necessário, mas apenas para manipular a imagem de template
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings # Para pegar o caminho da pasta static

def create_dynamic_stamp(signer_name: str) -> bytes:
    """
    Carrega uma imagem de template e escreve os dados dinâmicos sobre ela.
    """
    try:
        # Caminho para a imagem de template na sua pasta static
        template_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'stamp_template.png')
        stamp_img = Image.open(template_path).convert("RGBA")
        
        draw = ImageDraw.Draw(stamp_img)
        
        try:
            # Tenta carregar uma fonte bonita, se disponível
            font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arialbd.ttf", 11) # Bold para o nome
        except IOError:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Escreve o nome do assinante e a data na imagem
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        draw.text((80, 25), signer_name[:28], fill="black", font=font)
        draw.text((80, 55), f"Data: {now_str}", fill="black", font=small_font)

        # Converte a imagem final para bytes em memória
        img_byte_arr = os.BytesIO()
        stamp_img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    except Exception:
        # Se a criação da imagem falhar, retorna None para usar uma assinatura invisível
        return None

def process_sign_pdf(
    pdf_file_bytes: bytes,
    pfx_file_bytes: bytes,
    password: str,
    output_dir: str,
    base_filename: str,
    page_index: int = 0,
    x1: int = 50, y1: int = 50, x2: int = 300, y2: int = 150
) -> Tuple[bool, str, str, dict]:
    try:
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file_bytes, passphrase=password.encode('utf-8')
        )
        
        signature_meta = PdfSignatureMetadata(reason="Validade do Documento")

        # Extrai o nome do assinante do certificado
        try:
            common_name = signer.cert_registry.get_cert_by_id(signer.signing_cert.issuer_serial).subject.native['common_name']
        except:
            common_name = "Assinante"
        
        # Gera a imagem do carimbo dinamicamente
        stamp_bytes = create_dynamic_stamp(common_name)
        
        pdf_signer = PdfSigner(signature_meta, signer, appearance_img_bytes=stamp_bytes)

        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "wb") as f_out:
            pdf_signer.sign_pdf(
                os.BytesIO(pdf_file_bytes),
                output=f_out,
                appearance_field_name='Signature1',
                box=(x1, y1, x2, y2),
                on_page=page_index
            )

        return True, "Documento assinado com sucesso!", output_filename, None

    except SigningError as e:
        error_message = str(e)
        if "MAC failure" in error_message or "bad mac" in error_message:
            error_message = "Senha do certificado incorreta."
        return False, f"Erro de assinatura: {error_message}", "", None
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}", "", None