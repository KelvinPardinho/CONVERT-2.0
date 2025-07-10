# services/sign_pdf.py (VERSÃO FINAL GARANTIDA)

import os
import uuid
from datetime import datetime
from io import BytesIO

# Apenas os imports básicos e estáveis
from pyhanko.sign import signers
from pyhanko.pdf_utils.reader import PdfFileReader

def process_sign_pdf(
    pdf_bytes: bytes,
    pfx_bytes: bytes,
    password: str,
    signature_data: dict,
    output_dir: str,
    base_filename: str
) -> tuple:
    try:
        signer = signers.SimpleSigner.load_pfx(
            pfx_bytes, passphrase=password.encode()
        )

        signature_meta = signers.SignatureMetadata(
            reason="Assinatura Digital de Documento",
            location="Sao Paulo, Brazil",
            signer=signer.subject_name,
            signing_time=datetime.now()
        )
        
        pdf_signer = signers.PdfSigner(signature_meta, signer)
        output_buffer = BytesIO()
        
        pdf_signer.sign_pdf(
            PdfFileReader(BytesIO(pdf_bytes)),
            output=output_buffer
        )
        
        output_buffer.seek(0)

        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(output_buffer.read())

        return True, "Documento assinado com sucesso (sem aparência visual).", output_filename, {}

    except Exception as e:
        error_message = str(e)
        if "decryption failed" in error_message.lower() or "mac verify" in error_message.lower() or "bad password" in error_message.lower():
            return False, "Senha do certificado incorreta. Por favor, verifique e tente novamente.", None, {}
        
        print(f"ERRO CRÍTICO EM SIGN_PDF: {error_message}") 
        return False, f"Ocorreu um erro técnico ao assinar o PDF.", None, {}