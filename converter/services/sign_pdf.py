# services/sign_pdf.py (VERSÃO FINAL E CORRETA)

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
        signer = signers.SimpleSigner.load_pfx(pfx_bytes, passphrase=password.encode())
        
        pdf_writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
        
        page_index = signature_data.get('pageIndex', 0)
        x1, y1, x2, y2 = (
            signature_data.get('x1', 50),
            signature_data.get('y1', 50),
            signature_data.get('x2', 300),
            signature_data.get('y2', 150)
        )
        
        signature_field = signers.SignatureFieldSpec(
            sig_field_name=f'Signature-{uuid.uuid4().hex}',
            box=(x1, y1, x2, y2),
            on_page=page_index,
        )
        pdf_writer.add_signature_field(signature_field)

        output_buffer = BytesIO()
        signers.sign_pdf(
            pdf_writer,
            signers.SignatureMetadata(signing_time=datetime.now()),
            signer=signer,
            output=output_buffer,
            existing_fields_only=True
        )
        output_buffer.seek(0)

        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(output_buffer.read())

        return True, "Documento assinado com sucesso!", output_filename, {}

    except Exception as e:
        error_message = str(e)
        if "decryption failed" in error_message.lower() or "mac verify" in error_message.lower() or "bad password" in error_message.lower():
            return False, "Senha do certificado incorreta.", None, {}
        
        print(f"Erro inesperado no pyhanko: {error_message}")
        return False, f"Ocorreu um erro técnico ao assinar o PDF.", None, {}