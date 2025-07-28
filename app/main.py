import os
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pdf_outline_extractor import PDFOutlineExtractor

INPUT_DIR = "/app/input" if os.path.exists("/app/input") else "input"
OUTPUT_DIR = "/app/output" if os.path.exists("/app/output") else "output"

def process_pdf(pdf_file):
    try:
        extractor = PDFOutlineExtractor()
        result = extractor.extract(pdf_file)
        output_file = os.path.join(OUTPUT_DIR, f"{Path(pdf_file).stem}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Processed: {os.path.basename(pdf_file)}")
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

def main():
    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files sequentially for now to avoid multiprocessing issues
    for pdf_file in pdf_files:
        process_pdf(pdf_file)

if __name__ == "__main__":
    main() 