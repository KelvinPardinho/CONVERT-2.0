import os
import uuid
from typing import Tuple, Optional
from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader

def process_sign_pdf(
    pdf_file_bytes: bytes,
    pfx_file_bytes: bytes,
    password: str,
    output_dir: str,
    base_filename: str,
    signer_email: Optional[str] = None,
    reason: str = "Concordância com os termos.",
    location: str = "Online",
) -> Tuple[bool, str, str, dict]:
    """
    Assina digitalmente um arquivo PDF com um certificado A1.

    Args:
        pdf_file_bytes (bytes): Conteúdo do PDF a ser assinado.
        pfx_file_bytes (bytes): Conteúdo do arquivo de certificado (.pfx/.p12).
        password (str): Senha do certificado.
        output_dir (str): Diretório para salvar o PDF assinado.
        base_filename (str): Nome do arquivo original.
        signer_email (str, optional): Email do assinante.
        reason (str, optional): Razão da assinatura.
        location (str, optional): Local da assinatura.

    Returns:
        Tuple[bool, str, str, dict]: (sucesso, mensagem, nome_do_arquivo, dados_extras)
    """
    try:
        # Carrega o signer a partir do arquivo PFX (certificado A1)
        # A senha é convertida para bytes, como a biblioteca espera
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file_bytes, passphrase=password.encode('utf-8')
        )
        
        # Prepara o documento PDF para receber a assinatura
        pdf_writer = IncrementalPdfFileWriter(os.BytesIO(pdf_file_bytes))

        # Configura os metadados da assinatura
        signature_meta = signers.SignatureMetadata(
            reason=reason,
            location=location,
            signer=signer.subject_name,
            contact_info=signer_email,
        )

        # Realiza a assinatura
        # A biblioteca cuida de criar o campo de assinatura, assinar o hash do documento
        # e embutir o certificado e a assinatura no PDF.
        # Aqui, estamos adicionando uma assinatura visível na última página.
        # Para posições personalizadas, a lógica seria mais complexa.
        pdf_signer = signers.PdfSigner(
            signature_meta,
            signer=signer,
            # Configuração do carimbo de tempo (opcional, mas recomendado)
            # É preciso usar um serviço de TSA (Time Stamping Authority)
            # timestamper=signers.requests_timestamper(tsa_url='http://timestamp.digicert.com')
        )

        output_filename = f"{base_filename}_signed_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "wb") as f_out:
            pdf_signer.sign_pdf(
                pdf_writer,
                output=f_out,
                # Aparência da assinatura (opcional)
                # appearance=...
            )

        return True, "Documento assinado digitalmente com sucesso!", output_filename, None

    except Exception as e:
        # Erros comuns: senha incorreta, certificado inválido, etc.
        error_message = str(e)
        if "MAC failure" in error_message or "bad mac" in error_message:
            error_message = "Senha do certificado incorreta."
        elif "Could not deserialize" in error_message:
            error_message = "Arquivo de certificado inválido ou corrompido."
        
        return False, f"Erro ao assinar o PDF: {error_message}", "", None