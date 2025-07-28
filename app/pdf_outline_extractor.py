import os
import fitz  # PyMuPDF
from app.utils import clean_text, extract_features, load_heading_model, is_page_number, is_date, is_common_footer, has_heading_number
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

MIN_HEADING_LEN = 8  # Minimum length for heading text (unless numbered)
MIN_HEADING_WORDS = 2  # Minimum words for heading (unless numbered)
MERGE_DIST_Y = 10  # Max vertical distance to merge short headings
MERGE_DIST_X = 30  # Max horizontal distance to merge heading parts

class PDFOutlineExtractor:
    def __init__(self, model_path=MODEL_PATH):
        self.model = load_heading_model(model_path)

    def _is_valid_heading(self, text):
        # Accept if long enough or matches heading numbering
        if len(text) >= MIN_HEADING_LEN:
            return True
        if has_heading_number(text):
            return True
        if len(text.split()) >= MIN_HEADING_WORDS:
            return True
        return False

    def _normalize_text(self, text):
        return ' '.join(text.strip().split())

    def _detect_heading_level(self, span, all_spans):
        """Detect heading level based on font size and other features"""
        text = span['text'].strip()
        size = span['size']
        
        # Skip very short text that's unlikely to be a heading
        if len(text) < 3:
            return None
            
        # Skip common non-heading text
        if text.lower() in ['page', 'of', 'and', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'by']:
            return None
        
        # Try to use ML model first if available
        if self.model is not None:
            try:
                features = extract_features(span, all_spans)
                prediction = self.model.predict([features])[0]
                if prediction != 'O':  # 'O' means not a heading
                    return prediction
            except Exception as e:
                # Fall back to rule-based approach if ML fails
                pass
        
        # Rule-based fallback approach
        # Get all font sizes for relative comparison
        all_sizes = sorted(set(s['size'] for s in all_spans), reverse=True)
        
        # Check for numbered headings first
        if has_heading_number(text):
            # Count dots to determine level
            dot_count = text.count('.')
            if dot_count == 1:
                return "H1"
            elif dot_count == 2:
                return "H2"
            elif dot_count >= 3:
                return "H3"
        
        # Check for specific heading patterns
        if text.strip().lower() in ['revision history', 'table of contents', 'acknowledgements', 'references', 'summary', 'background', 'introduction', 'conclusion']:
            return "H1"
        
        # Check for all caps text (likely headings)
        if text.isupper() and len(text) > 3:
            if len(all_sizes) >= 2:
                if size == all_sizes[0]:
                    return "H1"
                elif size == all_sizes[1]:
                    return "H2"
            else:
                return "H1"
        
        # Use font size ranking with more sophisticated logic
        if len(all_sizes) >= 3:
            if size == all_sizes[0]:
                return "H1"
            elif size == all_sizes[1]:
                return "H2"
            elif size == all_sizes[2]:
                return "H3"
        elif len(all_sizes) == 2:
            if size == all_sizes[0]:
                return "H1"
            elif size == all_sizes[1]:
                return "H2"
        elif len(all_sizes) == 1:
            # If only one font size, check if text looks like a heading
            if len(text) >= 5 and not text.isdigit():
                return "H1"
        
        return None

    def _postprocess_headings(self, outline, filename=None):
        # Remove headings that are too short and not numbered
        filtered = [h for h in outline if self._is_valid_heading(h['text'])]
        
        # Sort by page, y, x for merging
        filtered.sort(key=lambda h: (h['page'], h.get('y', 0), h.get('x', 0) if 'x' in h else 0))
        
        # Merge consecutive heading spans on the same page if close in y/x
        merged = []
        prev = None
        for h in filtered:
            h['text'] = self._normalize_text(h['text'])
            if prev and h['page'] == prev['page'] and abs(h.get('y', 0) - prev.get('y', 0)) < MERGE_DIST_Y and abs(h.get('x', 0) - prev.get('x', 0)) < MERGE_DIST_X:
                prev['text'] = self._normalize_text(prev['text'] + ' ' + h['text'])
            else:
                merged.append(h)
                prev = h
        
        # Remove duplicates
        seen = set()
        unique_merged = []
        for h in merged:
            key = (h['text'], h['page'], h['level'])
            if key not in seen:
                seen.add(key)
                unique_merged.append(h)
        
        # Remove 'y' and 'x' from output
        for h in unique_merged:
            if 'y' in h:
                del h['y']
            if 'x' in h:
                del h['x']
        
        return unique_merged

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
                            
                            # Enhanced filtering for better noise reduction
                            if (is_page_number(text) or 
                                is_date(text) or 
                                is_common_footer(text) or
                                len(text.strip()) < 2 or
                                text.strip().isdigit() or
                                text.strip().lower() in ['page', 'of', 'total']):
                                continue
                                
                            spans.append({
                                'text': text,
                                'size': span['size'],
                                'flags': span['flags'],
                                'font': span['font'],
                                'page': page_num,
                                'bbox': span['bbox'],
                                'y': span['bbox'][1] if 'bbox' in span and len(span['bbox']) > 1 else 0,
                                'x': span['bbox'][0] if 'bbox' in span and len(span['bbox']) > 0 else 0
                            })
        
        # Title: largest text on first page
        first_page_spans = [s for s in spans if s['page'] == 0]
        title = ""
        if first_page_spans:
            title_span = max(first_page_spans, key=lambda s: s['size'])
            title = self._normalize_text(title_span['text'])
        
        # Detect headings using font size and other features
        outline = []
        for span in spans:
            level = self._detect_heading_level(span, spans)
            if level and len(span['text']) <= 200:  # Skip very long text
                outline.append({
                    "level": level,
                    "text": span['text'],
                    "page": span['page'],
                    "y": span.get('y', 0),
                    "x": span.get('x', 0)
                })
        
        # Post-process to filter/merge/suppress false positives
        outline = self._postprocess_headings(outline)
        
        return {
            "title": title,
            "outline": outline
        }

def extract_outline(pdf_path):
    extractor = PDFOutlineExtractor()
    return extractor.extract(pdf_path) 