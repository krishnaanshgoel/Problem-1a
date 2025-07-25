import os
import sys
import fitz
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from utils import clean_text, extract_features

INPUT_DIR = "/app/input" if os.path.exists("/app/input") else "input"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

X, y = [], []

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(os.path.join(INPUT_DIR, filename))
        spans = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")['blocks']
            for block in blocks:
                if block['type'] == 0:
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
        # Heuristic: cluster font sizes
        sizes = sorted(set(s['size'] for s in spans))
        if len(sizes) > 2:
            h1, h2 = sizes[-1], sizes[-2]
        elif len(sizes) == 2:
            h1, h2 = sizes[-1], sizes[-2]
        elif len(sizes) == 1:
            h1, h2 = sizes[0], sizes[0]
        else:
            continue
        for s in spans:
            features = extract_features(s)
            # Improved pseudo-labeling
            if s['size'] == h1:
                label = "H1"
            elif s['size'] == h2:
                label = "H2"
            elif ('Bold' in s['font'] and len(s['text']) < 50) or (s['text'].isupper() and len(s['text']) < 50) or (features[-1] == 1 and len(s['text']) < 50):
                label = "H2"
            else:
                label = "O"
            X.append(features)
            y.append(label)

# Train model
clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X, y)
dump(clf, MODEL_PATH)
print(f"Trained model saved to {MODEL_PATH}") 