import os
import json
from pathlib import Path
from app.pdf_outline_extractor import PDFOutlineExtractor
from multiprocessing import Pool, cpu_count

INPUT_DIR = "/app/input" if os.path.exists("/app/input") else "input"
OUTPUT_DIR = "/app/output" if os.path.exists("/app/output") else "output"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "pdf_outline_extractor.py")

def process_pdf(pdf_file):
    extractor = PDFOutlineExtractor()
    result = extractor.extract(pdf_file)
    output_file = os.path.join(OUTPUT_DIR, f"{Path(pdf_file).stem}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with Pool(min(cpu_count(), 8)) as pool:
        pool.map(process_pdf, pdf_files)

if __name__ == "__main__":
    main() 