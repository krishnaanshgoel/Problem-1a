import re
import numpy as np
from joblib import load

def clean_text(text):
    # Remove excessive whitespace and control characters
    return re.sub(r'\s+', ' ', text).strip()

def extract_features(span):
    text = span['text']
    # Assume a default page width for centeredness (can be improved with actual page width)
    page_width = 595  # A4 width in points
    bbox = span.get('bbox', [0, 0, 0, 0])
    x0, _, x1, _ = bbox
    text_width = x1 - x0
    center_margin = abs((page_width / 2) - (x0 + text_width / 2))
    is_centered = int(center_margin < page_width * 0.15)
    return [
        span['size'],
        int('Bold' in span['font']),
        int('Italic' in span['font']),
        len(text),
        span['flags'],
        int(text.isupper()),
        int(len(text) < 50),
        int(any(c.isdigit() for c in text)),
        is_centered
    ]

def load_heading_model(model_path):
    return load(model_path) 