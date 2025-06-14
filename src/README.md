# PDF Email Summarizer - Refactored Code Structure

This directory contains the refactored and modularized version of the PDF Email Summarizer. The original monolithic `email_summarizer.py` has been broken down into specialized modules for better maintainability, readability, and testing.

## 📁 Module Structure

### Core Modules

#### 1. `text_extractor.py`

**Purpose**: Handles all PDF text extraction functionality

- **`PDFTextExtractor`**: Main class for extracting text from PDFs
  - Supports both regular PDFs (using PyPDF2)
  - Supports image-based PDFs (using OCR with Tesseract and Poppler)
  - Automatic fallback from PyPDF2 to OCR when needed
- **`TextCleaner`**: Utility class for cleaning extracted text
  - Removes excessive whitespace
  - Filters out page numbers and headers/footers

#### 2. `email_parser.py`

**Purpose**: Parses and structures email content from extracted text

- **`EmailParser`**: Handles email content analysis
  - `extract_email_info()`: Extracts metadata (subject, from, to, date)
  - `split_email_threads()`: Splits concatenated emails into individual messages
  - Recognizes common email separators and patterns

#### 3. `ai_summarizer.py`

**Purpose**: AI-powered summarization using OpenAI API

- **`AISummarizer`**: Handles OpenAI integration
  - `summarize_with_openai()`: Generates AI summaries
  - `_generate_prompt()`: Creates optimized prompts for different summary types
  - Supports short, medium, and long summary formats
  - Graceful error handling and fallbacks

#### 4. `pdf_email_summarizer.py`

**Purpose**: Main orchestrator class that coordinates all components

- **`PDFEmailSummarizer`**: Primary interface for the application
  - Integrates all specialized modules
  - Handles the complete workflow: extract → clean → parse → summarize
  - Maintains backward compatibility with the original API
  - Optional AI summarizer loading (graceful degradation if not available)

#### 5. `cli.py`

**Purpose**: Command-line interface

- **`main()`**: Interactive CLI for the application
  - User-friendly prompts for summary type selection
  - Formatted output display
  - Error handling and user feedback

#### 6. `__init__.py`

**Purpose**: Package initialization and exports

- Makes the `src` directory a proper Python package
- Exports all public classes and functions
- Handles optional imports (e.g., AI summarizer dependencies)

#### 7. `email_summarizer.py` (Backward Compatibility)

**Purpose**: Maintains compatibility with existing code

- Imports and re-exports the refactored classes
- Allows existing code to work without changes
- Serves as a migration bridge

## 🏗️ Architecture Benefits

### 1. **Separation of Concerns**

- Each module has a single, well-defined responsibility
- Text extraction is separate from parsing and summarization
- Easy to modify or replace individual components

### 2. **Modularity**

- Components can be used independently
- Easy to unit test individual modules
- Facilitates code reuse across different applications

### 3. **Maintainability**

- Smaller, focused files are easier to understand and modify
- Clear module boundaries make debugging easier
- Reduced code duplication

### 4. **Extensibility**

- Easy to add new text extraction methods
- Simple to support additional AI providers
- Straightforward to add new output formats

### 5. **Error Handling**

- Graceful degradation when dependencies are missing
- Isolated error handling in each module
- Better error messages and user feedback

## 🚀 Parallel Processing Features

### Multi-Page PDF Optimization

The refactored code now includes **parallel processing capabilities** for handling multi-page PDF documents efficiently:

#### **Automatic Parallel Processing**

- **PyPDF2 Extraction**: Multiple pages processed simultaneously using ThreadPoolExecutor
- **OCR Processing**: Image-based PDF pages processed in parallel for faster OCR
- **Smart Detection**: Automatically activates for PDFs with more than 1 page
- **Resource Management**: Caps worker threads to prevent system overload (max 8 workers)

#### **Configuration Options**

```python
# Auto-detect optimal workers (uses CPU core count)
summarizer = PDFEmailSummarizer()

# Custom worker count
summarizer = PDFEmailSummarizer(max_workers=4)

# Runtime configuration
summarizer.set_parallel_workers(2)
workers = summarizer.get_parallel_workers()
```

#### **Performance Benefits**

- **Speed Improvement**: 2-4x faster for multi-page documents
- **OCR Acceleration**: Significant speedup for image-based PDFs
- **Scalability**: Performance scales with available CPU cores
- **Efficiency**: I/O bound operations parallelized effectively

#### **Safety Features**

- **Thread Safety**: Uses ThreadPoolExecutor for safe concurrent processing
- **Error Isolation**: Individual page failures don't affect other pages
- **Fallback**: Graceful degradation for single-page documents
- **Order Preservation**: Maintains correct page order in final output

---

## 🔧 Usage Examples

### Basic Usage (Backward Compatible)

```python
from src.email_summarizer import PDFEmailSummarizer

summarizer = PDFEmailSummarizer()
result = summarizer.summarize_pdf_emails("email.pdf", "medium")
print(result['summary'])
```

### Modular Usage

```python
from src.text_extractor import PDFTextExtractor, TextCleaner
from src.email_parser import EmailParser
from src.ai_summarizer import AISummarizer

# Extract text
extractor = PDFTextExtractor()
raw_text = extractor.extract_text_from_pdf("email.pdf")

# Clean and parse
cleaner = TextCleaner()
clean_text = cleaner.clean_email_text(raw_text)

parser = EmailParser()
emails = parser.split_email_threads(clean_text)

# Summarize
summarizer = AISummarizer()
summary = summarizer.summarize_with_openai(emails, "medium")
```

### Command Line Interface

```python
from src.cli import main
main()  # Interactive CLI
```

### Parallel Processing Usage

```python
# High-performance processing for large PDFs
summarizer = PDFEmailSummarizer(max_workers=4)
result = summarizer.summarize_pdf_emails("large_email.pdf")

# Configure workers at runtime
summarizer.set_parallel_workers(2)
print(f"Using {summarizer.get_parallel_workers()} workers")

# Text extraction with custom parallelism
extractor = PDFTextExtractor(max_workers=6)
text = extractor.extract_text_from_pdf("multi_page_email.pdf")
```

## 📦 Dependencies

### Core Dependencies (Required)

- `PyPDF2`: PDF text extraction
- `python-dotenv`: Environment variable management
- `typing`: Type hints support

### AI Dependencies (Optional)

- `openai`: OpenAI API integration

### OCR Dependencies (Optional)

- `pytesseract`: OCR text recognition
- `pdf2image`: PDF to image conversion
- `Pillow`: Image processing

### System Dependencies (for OCR)

- **Tesseract OCR**: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler**: Download from [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

## 🧪 Testing Structure

Each module can be tested independently:

```python
# Test text extraction
from src.text_extractor import PDFTextExtractor
extractor = PDFTextExtractor()
assert extractor.extract_text_from_pdf("test.pdf") != ""

# Test email parsing
from src.email_parser import EmailParser
parser = EmailParser()
emails = parser.split_email_threads("sample text")
assert len(emails) > 0

# Test AI summarization (requires API key)
from src.ai_summarizer import AISummarizer
summarizer = AISummarizer()
summary = summarizer.summarize_with_openai(emails)
assert summary != ""
```

## 🔄 Migration Guide

### From Original Code

If you're using the original `email_summarizer.py`, no changes are needed:

```python
# This still works
from src.email_summarizer import PDFEmailSummarizer
```

### To New Modular Structure

For new development, use the modular imports:

```python
# Recommended for new code
from src import PDFEmailSummarizer, PDFTextExtractor, EmailParser
```

## 🚀 Future Enhancements

The modular structure makes it easy to add:

- Support for additional file formats (Word, HTML, etc.)
- Multiple AI provider support (Anthropic, Cohere, etc.)
- Database storage for processed emails
- Web API interface
- Batch processing capabilities
- Custom email parsing rules
- Advanced OCR options

## 📝 Configuration

### Environment Variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### OCR Setup (Windows)

1. Install Tesseract: Download and install from the official repository
2. Install Poppler: Extract to a known location (e.g., `C:\poppler`)
3. Add both to your system PATH, or the application will try to find them automatically

This refactored structure provides a solid foundation for maintaining and extending the PDF Email Summarizer while preserving all existing functionality.
