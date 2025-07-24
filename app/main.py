import os
import json
from app.pdf_outline_extractor import extract_outline

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename[:-4] + ".json")
            try:
                outline = extract_outline(pdf_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(outline, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main() 