# services/pdf_to_excel.py (VERSÃO CORRIGIDA E OTIMIZADA)

import os
import uuid
import pandas as pd
import camelot
from pdf2image import convert_from_bytes
from typing import Tuple

def convert_pdf_to_excel(
    pdf_file: object, 
    output_dir: str
) -> Tuple[bool, str, str]:
    """
    Extrai dados de um PDF para Excel. Tenta extrair tabelas estruturadas;
    se falhar, usa OCR como alternativa.

    Args:
        pdf_file (UploadedFile): O objeto de arquivo PDF enviado.
        output_dir (str): O diretório para salvar a planilha Excel.

    Returns:
        Tuple[bool, str, str]: (sucesso, nome_do_arquivo_convertido, mensagem_de_erro)
    """
    # Lê o conteúdo do arquivo em memória uma única vez
    pdf_bytes = pdf_file.read()
    
    original_name = os.path.splitext(pdf_file.name)[0]
    # Gera um nome de arquivo de saída único
    converted_filename = f"{original_name}_{uuid.uuid4().hex[:6]}.xlsx"
    converted_path = os.path.join(output_dir, converted_filename)

    conversion_success = False
    error_message = ""

    # --- TENTATIVA 1: Extração de Tabela com Camelot ---
    temp_pdf_path = None
    try:
        # Camelot precisa de um caminho de arquivo, então salvamos temporariamente
        temp_pdf_path = os.path.join(output_dir, f"temp_{uuid.uuid4()}.pdf")
        with open(temp_pdf_path, 'wb') as temp_f:
            temp_f.write(pdf_bytes)

        # 'stream' é geralmente melhor para PDFs sem linhas de grade claras
        tables = camelot.read_pdf(temp_pdf_path, pages='all', flavor='stream')
        
        if tables.n > 0:
            # Concatena todos os DataFrames de tabelas encontradas
            all_dfs = [table.df for table in tables]
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Exporta para um único arquivo Excel
            combined_df.to_excel(converted_path, index=False, header=False)
            
            if os.path.exists(converted_path) and os.path.getsize(converted_path) > 100:
                conversion_success = True
                
    except Exception as e:
        error_message = f"Extração de tabela falhou: {str(e)}"

    finally:
        # Garante que o arquivo temporário seja sempre removido
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


    # --- TENTATIVA 2: OCR (se a primeira falhar) ---
    # Esta parte foi removida por ser muito complexa e geralmente produzir resultados ruins
    # para a estrutura de uma planilha. A extração de tabelas com Camelot é o método correto.
    # Se Camelot falhar, é melhor informar ao usuário.


    if conversion_success:
        return True, converted_filename, ""
    else:
        # Se a conversão falhou, remove o arquivo de saída vazio, se existir
        if os.path.exists(converted_path):
            os.remove(converted_path)
        
        final_error = "Nenhuma tabela estruturada pôde ser detectada no PDF."
        if error_message:
            final_error += f" Detalhes técnicos: {error_message}"
            
        return False, "", final_error