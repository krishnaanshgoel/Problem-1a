import os
import sys
import fitz
import numpy as np
import json
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from utils import clean_text, extract_features, is_page_number, is_date, is_common_footer

PDF_DIR = os.path.join(os.path.dirname(__file__), '../sample_dataset/pdfs')
OUT_DIR = os.path.join(os.path.dirname(__file__), '../sample_dataset/outputs')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

X, y = [], []

for filename in os.listdir(PDF_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_DIR, filename)
        json_path = os.path.join(OUT_DIR, filename.replace('.pdf', '.json'))
        if not os.path.exists(json_path):
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            gt = json.load(f)
        gt_headings = gt.get('outline', [])
        # Build a lookup for (page, cleaned text) -> level
        heading_lookup = {}
        for h in gt_headings:
            key = (h['page'], clean_text(h['text']))
            heading_lookup[key] = h['level']
        doc = fitz.open(pdf_path)
        spans = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text('dict')['blocks']
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            text = clean_text(span['text'])
                            if not text.strip():
                                continue
                            if is_page_number(text) or is_date(text) or is_common_footer(text):
                                continue
                            spans.append({
                                'text': text,
                                'size': span['size'],
                                'flags': span['flags'],
                                'font': span['font'],
                                'page': page_num,
                                'bbox': span['bbox']
                            })
        # Label spans using ground truth
        for s in spans:
            features = extract_features(s, spans)
            key = (s['page'], clean_text(s['text']))
            label = heading_lookup.get(key, 'O')
            X.append(features)
            y.append(label)

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
clf.fit(X, y)
dump(clf, MODEL_PATH)
print(f"Trained model saved to {MODEL_PATH}") 