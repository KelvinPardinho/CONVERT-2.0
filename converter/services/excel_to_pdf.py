import os
import uuid
import platform
from typing import Tuple

# A biblioteca comtypes é uma dependência do pywin32
if platform.system() == "Windows":
    import win32com.client
    import comtypes.client

# ... (suas outras funções de serviço) ...

def process_excel_to_pdf(excel_file, output_dir: str) -> Tuple[bool, str, str]:
    """
    Converte um ficheiro Excel (.xls ou .xlsx) para PDF usando a automação do Excel (Windows).

    Args:
        excel_file (UploadedFile): O objeto de ficheiro Excel enviado.
        output_dir (str): O diretório para salvar o ficheiro PDF de saída.

    Returns:
        Tuple[bool, str, str]: (sucesso, mensagem, nome_do_arquivo_pdf)
    """
    if platform.system() != "Windows":
        return False, "Esta funcionalidade só está disponível em servidores Windows com Microsoft Excel instalado.", ""

    temp_input_name = f"{uuid.uuid4().hex}_{excel_file.name}"
    input_path = os.path.abspath(os.path.join(output_dir, temp_input_name))

    base_filename = os.path.splitext(excel_file.name)[0]
    output_filename = f"{base_filename}.pdf"
    output_path = os.path.abspath(os.path.join(output_dir, output_filename))

    comtypes.CoInitialize()
    excel_app = None
    workbook = None
    try:
        # Salva o ficheiro Excel temporariamente no disco
        with open(input_path, 'wb+') as f:
            for chunk in excel_file.chunks():
                f.write(chunk)
        
        # Inicia a aplicação Excel
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = False # Executa em segundo plano

        # Abre a folha de cálculo
        workbook = excel_app.Workbooks.Open(input_path)

        # Converte o workbook inteiro para PDF (Tipo 0)
        workbook.ExportAsFixedFormat(0, output_path)

        return True, "Ficheiro Excel convertido para PDF com sucesso!", output_filename

    except Exception as e:
        error_message = f"Ocorreu um erro ao converter o Excel: {str(e)}. Verifique se o Microsoft Excel está instalado no servidor."
        return False, error_message, ""
        
    finally:
        # Bloco CRUCIAL para garantir que os processos do Excel sejam encerrados
        if workbook:
            workbook.Close(False) # Fecha sem salvar alterações
        if excel_app:
            excel_app.Quit()
        if os.path.exists(input_path):
            os.remove(input_path)
            
        comtypes.CoUninitialize()