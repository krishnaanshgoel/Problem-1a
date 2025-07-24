# PDF Outline Extractor

## Overview
This solution extracts a structured outline (title, H1, H2, H3 headings with page numbers) from PDF files, outputting a JSON for each PDF. It is designed for speed, accuracy, and modularity, and runs fully offline in a Docker container.

## Approach
- **PDF Parsing:** Uses PyMuPDF to extract text, font sizes, and styles.
- **Heading Detection:** Heuristically assigns heading levels based on font size ranking (largest = H1, next = H2, etc.), with helpers for text cleaning and normalization.
- **Title Extraction:** The largest text on the first page is assumed to be the document title.
- **Performance:** Lightweight, no network calls, and processes a 50-page PDF in under 10 seconds.

## How to Build and Run
1. **Build the Docker image:**
   ```sh
   docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
   ```
2. **Run the container:**
   ```sh
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
   ```
   - Place your PDFs in the `input/` directory. Output JSONs will appear in `output/`.

## Improving the Solution
- **Heading Detection:**
  - Incorporate font weight, bold/italic, and position (e.g., centered) for more robust heading detection.
  - Use text patterns (e.g., numbering, all caps) to supplement font size.
  - For multilingual support, ensure Unicode handling and test with non-Latin scripts.
- **Performance:**
  - Profile and optimize PDF parsing for large/complex documents.
- **Testing:**
  - Add more sample PDFs (varied layouts, languages) to the `input/` folder and compare outputs to ground truth.
- **Extensibility:**
  - Modularize heading detection logic for easy upgrades in future rounds.

## Dependencies
- Python 3.10+
- PyMuPDF

## Contact
For questions or improvements, please reach out to the author. 