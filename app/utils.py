import re

def clean_text(text):
    # Remove excessive whitespace and control characters
    return re.sub(r'\s+', ' ', text).strip()

def detect_heading_level(size, heading_sizes):
    # Assign H1, H2, H3 based on font size ranking
    if not heading_sizes:
        return None
    if size == heading_sizes[0]:
        return "H1"
    elif len(heading_sizes) > 1 and size == heading_sizes[1]:
        return "H2"
    elif len(heading_sizes) > 2 and size == heading_sizes[2]:
        return "H3"
    return None 