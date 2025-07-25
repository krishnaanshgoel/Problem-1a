import fitz  # PyMuPDF
from app.utils import clean_text, extract_features, load_heading_model
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

class PDFOutlineExtractor:
    def __init__(self, model_path=MODEL_PATH):
        self.model = load_heading_model(model_path)

    def extract(self, pdf_path):
        doc = fitz.open(pdf_path)
        spans = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")['blocks']
            for block in blocks:
                if block['type'] == 0:  # text block
                    for line in block['lines']:
                        for span in line['spans']:
                            text = clean_text(span['text'])
                            if not text.strip():
                                continue
                            spans.append({
                                'text': text,
                                'size': span['size'],
                                'flags': span['flags'],
                                'font': span['font'],
                                'page': page_num,
                                'bbox': span['bbox']
                            })
        # Title: largest text on first page
        first_page_spans = [s for s in spans if s['page'] == 0]
        title_span = max(first_page_spans, key=lambda s: s['size'], default={"text": ""})
        title = title_span['text']
        # Feature extraction for ML
        X = np.array([extract_features(s) for s in spans])
        preds = self.model.predict(X) if len(X) > 0 else []
        outline = []
        for s, pred in zip(spans, preds):
            if pred in ("H1", "H2", "H3"):
                outline.append({
                    "level": pred,
                    "text": s["text"],
                    "page": s["page"]
                })
        return {
            "title": title,
            "outline": outline
        }

def extract_outline(pdf_path):
    extractor = PDFOutlineExtractor()
    return extractor.extract(pdf_path) 