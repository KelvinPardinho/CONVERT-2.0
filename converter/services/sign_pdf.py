import os
import uuid
from datetime import datetime
from io import BytesIO

# Imports corretos e necessários para a versão atual do pyhanko
from pyhanko.sign import signers
from pyhanko.pdf_utils.writer import IncrementalPdfFileWriter
# O PdfFileReader não é necessário neste fluxo, então foi removido.

def process_sign_pdf(
    pdf_bytes: bytes,
    pfx_bytes: bytes,
    password: str,
    signature_data: dict,
    output_dir: str,
    base_filename: str
) -> tuple:
    try:
        # 1. Carrega o assinante a partir do arquivo PFX
        signer = signers.SimpleSigner.load_pfx(
            pfx_bytes, passphrase=password.encode()
        )

        # 2. Prepara o escritor de PDF
        pdf_writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
        
        # 3. Extrai os dados de posicionamento da assinatura
        page_index = signature_data.get('pageIndex', 0)
        x1 = signature_data.get('x1', 50)
        y1 = signature_data.get('y1', 50)
        x2 = signature_data.get('x2', 300)
        y2 = signature_data.get('y2', 150)
        
        # 4. Adiciona o campo de assinatura ao PDF
        # O pyhanko cria um campo de assinatura vazio primeiro
        signature_field_name = signers.SignatureFieldSpec(
            sig_field_name=f'Signature-{uuid.uuid4().hex}',
            box=(x1, y1, x2, y2),
            on_page=page_index,
        )
        pdf_writer.add_signature_field(signature_field_name)

        # 5. Preenche o campo de assinatura com a assinatura digital
        signed_pdf_buffer = signers.sign_pdf(
            pdf_writer,
            signers.SignatureMetadata(signing_time=datetime.now()),
            signer=signer,
            existing_fields_only=True, # Assina apenas o campo que acabamos de criar
        )

        # 6. Salva o arquivo final no disco
        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(signed_pdf_buffer.read())

        # Retorna o dicionário de dados extra vazio, conforme a assinatura da função
        return True, "Documento assinado com sucesso!", output_filename, {}

    except Exception as e:
        error_message = str(e)
        if "decryption failed" in error_message.lower() or "mac verify" in error_message.lower() or "bad password" in error_message.lower():
            return False, "Senha do certificado incorreta. Por favor, verifique e tente novamente.", None, {}
        
        print(f"Erro inesperado no pyhanko: {error_message}") 
        return False, f"Ocorreu um erro ao assinar o PDF. Verifique os logs do servidor.", None, {}