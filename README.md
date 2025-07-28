# PDF Outline Extractor

## Overview
A sophisticated PDF outline extraction tool that automatically identifies and extracts document titles and hierarchical headings (H1, H2, H3) from PDF files. The solution outputs structured JSON data containing the document title and a detailed outline with page numbers for each heading level.

## Features
- **Intelligent Heading Detection**: Uses font size analysis, text patterns, and machine learning to accurately identify heading levels
- **Title Extraction**: Automatically extracts document titles from the first page
- **Page Number Mapping**: Associates each heading with its corresponding page number
- **Text Cleaning**: Removes noise, normalizes text, and merges fragmented headings
- **Offline Processing**: Works completely offline without external API dependencies
- **Docker Support**: Containerized solution for easy deployment and consistency
- **Performance Optimized**: Processes large PDFs efficiently with minimal resource usage

## Technical Architecture

### Core Components
- **PDFOutlineExtractor**: Main extraction engine using PyMuPDF for PDF parsing
- **Heading Detection Algorithm**: Multi-factor analysis combining font size, position, and text patterns
- **Machine Learning Model**: Pre-trained model for enhanced heading classification (optional)
- **Text Processing Pipeline**: Cleaning, normalization, and merging of text spans

### Heading Detection Logic
1. **Font Size Analysis**: Ranks text by font size to determine heading hierarchy
2. **Pattern Recognition**: Identifies numbered headings (1., 1.1., 2.3.4., etc.)
3. **Position Analysis**: Considers text positioning (centered, left-aligned)
4. **Text Features**: Analyzes capitalization, word count, and special formatting
5. **Post-processing**: Merges fragmented headings and removes duplicates

## Project Structure
```
├── app/
│   ├── main.py                    # Main execution script
│   ├── pdf_outline_extractor.py   # Core extraction logic
│   ├── utils.py                   # Utility functions and text processing
│   ├── train_heading_model.py     # ML model training script
│   ├── compare_outputs.py         # Output validation tool
│   ├── model.pkl                  # Pre-trained heading classification model
│   └── __init__.py
├── input/                         # Input PDF files directory
├── output/                        # Generated JSON output files
├── sample_dataset/
│   ├── pdfs/                      # Sample PDF files for testing
│   ├── outputs/                   # Expected output files
│   └── schema/                    # JSON schema definition
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker container configuration
└── README.md                      # This file
```

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Docker (optional, for containerized execution)

### Local Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pdf-outline-extractor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Place PDF files** in the `input/` directory

4. **Run the extractor**:
   ```bash
   python app/main.py
   ```

### Docker Installation
1. **Build the Docker image**:
   ```bash
   docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
   ```

2. **Run the container**:
   ```bash
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:latest
   ```

   **Windows PowerShell**:
   ```powershell
   docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-outline-extractor:latest
   ```

## Usage

### Input
- Place PDF files in the `input/` directory
- Supported formats: PDF files with text content
- The tool processes all `.pdf` files in the input directory

### Output
For each input PDF, a corresponding JSON file is generated in the `output/` directory with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Heading",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Sub Heading",
      "page": 2
    }
  ]
}
```

### Output Schema
- **title**: String containing the extracted document title
- **outline**: Array of heading objects
  - **level**: Heading level ("H1", "H2", "H3")
  - **text**: Heading text content
  - **page**: Page number where the heading appears


## Testing & Validation

### Sample Dataset
The project includes a comprehensive sample dataset with:
- 5 test PDF files with varying layouts and complexity
- Expected output files for validation
- JSON schema definition for output validation

### Running Tests
1. **Process sample files**:
   ```bash
   cp sample_dataset/pdfs/* input/
   python app/main.py
   ```

2. **Compare outputs**:
   ```bash
   python app/compare_outputs.py
   ```

3. **Validate schema**:
   ```bash
   # Use a JSON schema validator to check output against schema
   ```

## Advanced Features

### Machine Learning Model
The solution includes an optional pre-trained machine learning model (`model.pkl`) that enhances heading detection by analyzing:
- Font characteristics (size, weight, style)
- Text positioning and alignment
- Text patterns and formatting
- Relative size relationships

### Text Processing Pipeline
1. **Noise Removal**: Filters out page numbers, dates, and common footer text
2. **Text Normalization**: Cleans whitespace and control characters
3. **Heading Merging**: Combines fragmented heading spans
4. **Duplicate Removal**: Eliminates redundant headings

### Heading Classification
The system uses multiple strategies for heading level detection:
- **Numbered Headings**: Automatic level detection based on numbering depth
- **Font Size Ranking**: Relative size comparison across the document
- **Pattern Matching**: Recognition of common heading patterns
- **Position Analysis**: Consideration of text positioning and alignment

