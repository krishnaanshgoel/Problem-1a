import fitz  # PyMuPDF
from app.utils import clean_text, detect_heading_level

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    headings = []
    font_stats = []
    title = None
    # Pass 1: Collect font sizes and styles for heuristics
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
                        font_stats.append({
                            'size': span['size'],
                            'flags': span['flags'],
                            'font': span['font'],
                            'text': text,
                            'page': page_num + 1
                        })
    # Heuristic: Largest text on first page is title
    first_page_fonts = [f for f in font_stats if f['page'] == 1]
    if first_page_fonts:
        title_span = max(first_page_fonts, key=lambda x: x['size'])
        title = title_span['text']
    # Cluster font sizes for heading levels
    sizes = sorted(set(f['size'] for f in font_stats))
    if len(sizes) > 3:
        # Use top 3 largest as H1, H2, H3
        heading_sizes = sizes[-3:][::-1]
    else:
        heading_sizes = sizes[::-1]
    # Pass 2: Extract headings
    for f in font_stats:
        level = detect_heading_level(f['size'], heading_sizes)
        if level:
            headings.append({
                'level': level,
                'text': f['text'],
                'page': f['page']
            })
    return {
        'title': title or "",
        'outline': headings
    } 