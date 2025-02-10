# Medical Guidelines OCR Pipeline

A specialized OCR pipeline for extracting and structuring medical guidelines from images, integrated with the Triage project's data schema.

## Quick Start

1. **Switch to the OCR branch**:
```bash
git checkout guideocrpipe
```

2. **Install Tesseract OCR**:
- Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

3. **Install dependencies** (using existing Poetry environment):
```bash
poetry add pytesseract pillow opencv-python numpy beautifulsoup4 requests
```

4. **Run the example**:
```bash
poetry run python src/example_usage.py
```

## Components

- **OCR Pipeline**: Handles image processing and text extraction
- **Guideline Interpreter**: Structures extracted text into standardized formats
- **Medical Guideline Scraper**: Collects guideline images from medical sources

## Integration

This pipeline works with the main Triage project by:
1. Following the established data schemas
2. Using the existing Poetry environment
3. Supporting the FastAPI backend
4. Generating chat-compatible outputs

## Development

1. **Add new features**:
   - Add regex patterns in `guideline_interpreter.py`
   - Modify preprocessing in `ocr_pipeline.py`
   - Update schema templates in `schemas/`

2. **Testing**:
   ```bash
   poetry run pytest tests/
   ```

## Next Steps

- [ ] Add batch processing support
- [ ] Implement PDF handling
- [ ] Add more medical terminology patterns
- [ ] Improve confidence scoring
- [ ] Add unit tests
- [ ] Create API endpoints for OCR service 