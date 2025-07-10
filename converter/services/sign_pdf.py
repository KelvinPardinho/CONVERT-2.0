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
        # 1. Carrega o assinante do certificado PFX
        signer = signers.SimpleSigner.load_pfx(
            pfx_bytes, passphrase=password.encode()
        )

        # 2. Prepara o escritor de PDF
        pdf_writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
        
        # 3. Assina o documento sem adicionar uma aparência visual
        output_buffer = signers.sign_pdf(
            pdf_writer,
            signers.SignatureMetadata(signing_time=datetime.now()),
            signer=signer,
        )

        # 4. Salva o resultado no disco
        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(output_buffer.read())

        return True, "Documento assinado com sucesso! (Assinatura digital aplicada sem carimbo visual)", output_filename, {}

    except Exception as e:
        error_message = str(e)
        if "decryption failed" in error_message.lower() or "mac verify" in error_message.lower() or "bad password" in error_message.lower():
            return False, "Senha do certificado incorreta. Por favor, verifique e tente novamente.", None, {}
        
        # Loga o erro real no servidor para podermos ver
        print(f"ERRO CRÍTICO EM SIGN_PDF: {error_message}") 
        return False, f"Ocorreu um erro técnico ao assinar o PDF.", None, {}