import re
import numpy as np
from joblib import load

def clean_text(text):
    # Remove excessive whitespace and control characters
    return re.sub(r'\s+', ' ', text).strip()

def is_page_number(text):
    return bool(re.match(r'^(page\s*\d+(\s*of\s*\d+)?)$', text.strip(), re.I)) or text.strip().isdigit()

def is_date(text):
    # Simple date pattern (e.g., 18 JUNE 2013, 23/07/2013, 2013-07-23)
    return bool(re.search(r'(\d{1,2}[\-/ ]\w{3,9}[\-/ ]\d{2,4})|(\d{4}[\-/]\d{2}[\-/]\d{2})', text))

def is_common_footer(text):
    # Add more patterns as needed
    return is_page_number(text) or is_date(text) or 'copyright' in text.lower()

def has_heading_number(text):
    # Only match section numbers like 1., 1.1, 2.3.4, 1.1.
    return int(bool(re.match(r'^(\d+\.)+(\d+)?\s*$', text.strip())))

def is_title_case(text):
    words = text.split()
    if not words:
        return 0
    return int(all(w[0].isupper() for w in words if w[0].isalpha()))

def extract_features(span, all_spans=None):
    text = span['text']
    page_width = 595  # A4 width in points
    bbox = span.get('bbox', [0, 0, 0, 0])
    x0, y0, x1, y1 = bbox
    text_width = x1 - x0
    center_margin = abs((page_width / 2) - (x0 + text_width / 2))
    is_centered = int(center_margin < page_width * 0.15)
    y_pos = y0  # y-position (top of text)
    word_count = len(text.split())
    is_title = is_title_case(text)
    has_number = has_heading_number(text)
    # Relative font size features
    size = span['size']
    if all_spans is not None and len(all_spans) > 0:
        all_sizes = [s['size'] for s in all_spans]
        max_size = max(all_sizes)
        min_size = min(all_sizes)
        median_size = np.median(all_sizes)
        rel_size_max = size / max_size if max_size else 0
        rel_size_median = size / median_size if median_size else 0
    else:
        rel_size_max = rel_size_median = 1.0
    align_left = int(x0 < page_width * 0.2)
    align_right = int(x1 > page_width * 0.8)
    return [
        size,
        rel_size_max,
        rel_size_median,
        int('Bold' in span['font']),
        int('Italic' in span['font']),
        len(text),
        span['flags'],
        int(text.isupper()),
        int(len(text) < 50),
        int(any(c.isdigit() for c in text)),
        is_centered,
        y_pos,
        word_count,
        is_title,
        has_number,
        align_left,
        align_right
    ]

def load_heading_model(model_path):
    return load(model_path) 