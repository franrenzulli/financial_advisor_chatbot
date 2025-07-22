import fitz  # PyMuPDF
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Procesador de documentos PDF"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )
        logger.info(f"PDFProcessor inicializado con chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    
    def process_pdf_content(self, pdf_data, key):
        """
        Procesa el contenido de un PDF y lo convierte en documentos
        
        Args:
            pdf_data (bytes): Contenido del PDF
            key (str): Clave del archivo en S3
            
        Returns:
            tuple: (lista_documentos, error_mensaje)
        """
        try:
            if not isinstance(pdf_data, (bytes, bytearray)):
                raise ValueError("Contenido descargado no es de tipo bytes.")
            
            docs = []
            chunk_count = 0
            
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf:
                for page_num, page in enumerate(pdf):
                    page_text = page.get_text()
                    
                    if page_text.strip():
                        chunks = self.text_splitter.split_text(page_text)
                        chunk_count += len(chunks)
                        
                        page_docs = [
                            Document(
                                page_content=chunk,
                                metadata={"source": key, "page": page_num}
                            ) for chunk in chunks
                        ]
                        docs.extend(page_docs)
            
            logger.info(f"✅ [{key}] {chunk_count} fragmentos generados")
            return docs, None
            
        except Exception as e:
            error_msg = f"Error procesando {key}: {str(e)}"
            logger.error(error_msg)
            return [], error_msg
    
    def validate_pdf_content(self, pdf_data):
        """
        Valida que el contenido sea un PDF válido
        
        Args:
            pdf_data (bytes): Contenido del PDF
            
        Returns:
            bool: True si es válido, False si no
        """
        try:
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf:
                return len(pdf) > 0
        except Exception:
            return False