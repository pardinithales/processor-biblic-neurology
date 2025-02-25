import pdfplumber
from PIL import Image
import io
import os

def clamp_bbox(bbox, page_width, page_height):
    """Ajusta as coordenadas do bounding box para ficar dentro dos limites da página."""
    x0, top, x1, bottom = bbox
    x0 = max(0, min(x0, page_width))
    top = max(0, min(top, page_height))
    x1 = max(0, min(x1, page_width))
    bottom = max(0, min(bottom, page_height))  # Corrigido 'custom' para 'bottom'
    return (x0, top, x1, bottom)

def extract_from_pdf(file_path):
    text = ""
    tables_text = ""
    images = []
    
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            if page_text:
                text += page_text + "\n"
            else:
                page_img = page.to_image(resolution=300)
                page_pil = page_img.original
                images.append(page_pil)
            
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                # Converte None para "" e junta os elementos da linha
                table_str = "\n".join([" ".join(str(cell) if cell is not None else "" for cell in row) for row in table if row])
                tables_text += f"Tabela {j + 1} (Página {i + 1}): {table_str}\n"
            
            page_width, page_height = page.width, page.height
            for k, img in enumerate(page.images):
                try:
                    bbox = clamp_bbox(
                        (img["x0"], img["top"], img["x1"], img["bottom"]),
                        page_width,
                        page_height
                    )
                    img_obj = page.within_bbox(bbox)
                    if img_obj:
                        img_data = img_obj.to_image()
                        img_pil = img_data.original
                        images.append(img_pil)
                except ValueError as e:
                    text += f"Imagem {k + 1} (Página {i + 1}): [Erro ao extrair imagem: {str(e)}]\n"
    
    return {"text": f"{text}\n\n{tables_text}".strip(), "images": images}

def extract_text_input(text_input):
    return {"text": text_input.strip(), "images": []}