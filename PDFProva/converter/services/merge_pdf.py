import os
from typing import List, Tuple, Any
from PyPDF2 import PdfWriter, PdfReader

def process_merge_pdf(
    pdf_files: List[Any],
    rotations: List[int], # << NOVO PARÂMETRO
    output_dir: str,
    output_filename: str = "merged_document.pdf"
) -> Tuple[bool, str, str]:
    """
    Combina múltiplos arquivos PDF, aplicando rotações a cada arquivo antes de unir.
    """
    merger = PdfWriter()
    
    try:
        # Itera sobre os arquivos e suas respectivas rotações
        for i, pdf_file in enumerate(pdf_files):
            reader = PdfReader(pdf_file)
            
            # Pega o ângulo de rotação para este arquivo. Se não houver, assume 0.
            angle = rotations[i] if i < len(rotations) else 0
            
            # Adiciona as páginas, aplicando a rotação se necessário
            for page in reader.pages:
                if angle % 360 != 0:
                    page.rotate(angle)
                merger.add_page(page)

        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f_out:
            merger.write(f_out)
        
        merger.close()
        
        return (True, "PDFs unidos com sucesso!", output_filename)

    except Exception as e:
        merger.close()
        return (False, f"Ocorreu um erro ao unir os PDFs: {str(e)}", "")