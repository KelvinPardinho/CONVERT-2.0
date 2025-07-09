import os
import uuid
from datetime import datetime
from io import BytesIO
from pyhanko.sign import signers
from pyhanko.pdf_utils.writer import IncrementalPdfFileWriter

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

        # 2. Define os metadados da assinatura
        signature_meta = signers.SignatureMetadata(
            reason="Assinatura Digital de Documento",
            location="Sao Paulo, Brazil",
            signer=signer.subject_name,
            signing_time=datetime.now()
        )
        
        # 3. Extrai os dados de posicionamento da assinatura
        page_index = signature_data.get('pageIndex', 0)
        x1 = signature_data.get('x1', 50)
        y1 = signature_data.get('y1', 50)
        x2 = signature_data.get('x2', 300)
        y2 = signature_data.get('y2', 150)
        
        # 4. Cria uma instância do PdfSigner com os metadados
        pdf_signer = signers.PdfSigner(signature_meta, signer)

        # 5. Salva o PDF assinado em um buffer de memória
        output_buffer = BytesIO()

        pdf_signer.sign_pdf(
            BytesIO(pdf_bytes),  
            output=output_buffer, 
            appearance=signers.PdfSignatureAppearance(
                box=(x1, y1, x2, y2),
                page=page_index,
            )
        )
        
        output_buffer.seek(0)

        # 6. Salva o buffer final no disco
        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(output_buffer.read())

        return True, "Documento assinado com sucesso!", output_filename, {}

    except Exception as e:
        error_message = str(e)
        if "decryption failed" in error_message.lower() or "mac verify" in error_message.lower() or "bad password" in error_message.lower():
            return False, "Senha do certificado incorreta. Por favor, verifique e tente novamente.", None, {}
        
        print(f"Erro inesperado no pyhanko: {error_message}") 
        return False, f"Ocorreu um erro ao assinar o PDF. Por favor, contate o suporte.", None, {}