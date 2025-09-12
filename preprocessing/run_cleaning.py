import os
import pdfplumber
from PyPDF2 import PdfReader
from text_cleaning import clean_text

try:
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models
    MARKER_AVAILABLE = True
    print("Marker is available")
except ImportError as e:
    print(f"Marker not available ({e}), using fallback libraries")
    MARKER_AVAILABLE = False

RAW_DIR = "data/"
CLEANED_DIR = "data/cleaned/"
IMAGES_DIR = "data/images/"

os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def extract_text_with_marker(pdf_path: str) -> tuple[str, list, dict]:
    if not MARKER_AVAILABLE:
        raise ImportError("Marker not available")
    
    try:
        model_lst = load_all_models()
        full_text, images, metadata = convert_single_pdf(pdf_path, model_lst)
        return full_text, images, metadata
    except Exception as e:
        try:
            full_text, images, metadata = convert_single_pdf(pdf_path)
            return full_text, images, metadata
        except Exception as e2:
            raise Exception(f"Marker failed: {e}, {e2}")

def extract_text_with_pdfplumber(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text

def extract_text_with_pypdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def process_pdf(pdf_path: str) -> tuple[str, list, dict]:
    if MARKER_AVAILABLE:
        try:
            return extract_text_with_marker(pdf_path)
        except Exception as e:
            print(f"Marker failed for {pdf_path}: {e}")
    
    try:
        text = extract_text_with_pdfplumber(pdf_path)
        return text, [], {"extractor": "pdfplumber"}
    except Exception as e:
        print(f"pdfplumber failed for {pdf_path}: {e}")
    
    try:
        text = extract_text_with_pypdf(pdf_path)
        return text, [], {"extractor": "pypdf2"}
    except Exception as e:
        print(f"PyPDF2 also failed for {pdf_path}: {e}")
        return "", [], {"error": str(e)}

def save_images(images: list, pdf_name: str) -> None:
    if not images:
        return
    
    pdf_images_dir = os.path.join(IMAGES_DIR, pdf_name)
    os.makedirs(pdf_images_dir, exist_ok=True)
    
    for i, image in enumerate(images):
        image_path = os.path.join(pdf_images_dir, f"image_{i+1}.png")
        try:
            image.save(image_path)
            print(f"Saved image: {image_path}")
        except Exception as e:
            print(f"Failed to save image {i+1}: {e}")

def run_pipeline():
    pdf_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {RAW_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    print(f"Using {'Marker' if MARKER_AVAILABLE else 'fallback libraries'}")
    print("=" * 60)
    
    for fname in pdf_files:
        pdf_path = os.path.join(RAW_DIR, fname)
        pdf_name = fname.replace(".pdf", "")
        
        print(f"\nProcessing: {fname}")
        raw_text, images, metadata = process_pdf(pdf_path)
        
        if not raw_text:
            print(f"Failed to extract any text from {fname}")
            continue
        try:
            cleaned_text = clean_text(raw_text)
            print(f"Text cleaned successfully")
        except Exception as e:
            print(f"Text cleaning failed: {e}")
            cleaned_text = raw_text  # Use raw text if cleaning fails
        
        output_path = os.path.join(CLEANED_DIR, f"{pdf_name}.txt")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            print(f"Text saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save text: {e}")
            continue
        
        if images:
            print(f"Found {len(images)} image(s)")
            save_images(images, pdf_name)
        
        extractor = metadata.get('extractor', 'marker')
        print(f"Extractor used: {extractor}")
        print(f"Text length: {len(cleaned_text):,} characters")
        
        if 'pages' in metadata:
            print(f"Pages processed: {metadata['pages']}")

if __name__ == "__main__":
    run_pipeline()





"""
import os
from langchain_docling import DoclingLoader
from text_cleaning import clean_text

RAW_DIR = "data/"
CLEANED_DIR = "data/cleaned/"   

os.makedirs(CLEANED_DIR, exist_ok=True)

def process_pdf_with_docling(pdf_path: str) -> str:
    loader = DoclingLoader(pdf_path)
    docs = loader.load()
    full_text = "\n".join(doc.page_content for doc in docs if doc.page_content)
    return full_text

def run_pipeline():
    pdf_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {RAW_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process with Docling")
    print("=" * 60)
    
    for fname in pdf_files:
        pdf_path = os.path.join(RAW_DIR, fname)
        pdf_name = fname.replace(".pdf", "")
        
        print(f"\nProcessing: {fname}")
        try:
            raw_text = process_pdf_with_docling(pdf_path)
            if not raw_text.strip():
                print(f"No text extracted from {fname} using Docling")
                continue
    
        except Exception as e:
            print(f"Failed to process {fname} with Docling: {e}")
            continue
        try:
            cleaned_text = clean_text(raw_text)
            print(f"Text cleaned successfully")
        except Exception as e:
            print(f"Text cleaning failed: {e}")
            cleaned_text = raw_text

        output_path = os.path.join(CLEANED_DIR, f"{pdf_name}.txt")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            print(f"Text saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save text: {e}")

if __name__ == "__main__":
    run_pipeline()
"""
