"""
Text extraction module for PDF files.
Handles both regular PDFs and image-based PDFs using OCR.
Supports parallel processing for multi-page PDFs.
"""

import PyPDF2
import os
import re
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing


class PDFTextExtractor:
    """Handles text extraction from PDF files using PyPDF2 and OCR fallback."""

    def __init__(self, max_workers: Optional[int] = None):
        self.ocr_available = self._check_ocr_availability()
        # Use number of CPU cores, but cap at 8 to avoid system overload
        self.max_workers = min(max_workers or multiprocessing.cpu_count(), 8)

    def _check_ocr_availability(self) -> bool:
        """Check if OCR libraries are available."""
        try:
            import pytesseract
            from pdf2image import convert_from_path

            return True
        except ImportError:
            return False

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file with parallel processing"""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # For single page, process directly
                if len(pdf_reader.pages) == 1:
                    text = pdf_reader.pages[0].extract_text()
                # For multiple pages, use parallel processing
                else:
                    text = self._extract_pages_parallel(pdf_reader.pages)

                # If no text was extracted, try OCR
                if not text.strip() and self.ocr_available:
                    print("No text found with PyPDF2, trying OCR...")
                    text = self._extract_text_with_ocr(pdf_path)
                elif not text.strip():
                    return ""

                return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            # Try OCR as fallback
            if self.ocr_available:
                try:
                    print("Trying OCR as fallback...")
                    return self._extract_text_with_ocr(pdf_path)
                except Exception as ocr_e:
                    print(f"OCR also failed: {str(ocr_e)}")
            return ""

    def _extract_pages_parallel(self, pages) -> str:
        """Extract text from multiple pages in parallel"""
        print(f"Processing {len(pages)} pages in parallel...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all pages for processing
            future_to_page = {
                executor.submit(self._extract_single_page, page, i): i
                for i, page in enumerate(pages)
            }

            # Collect results in order
            page_texts = [""] * len(pages)
            for future in as_completed(future_to_page):
                page_index = future_to_page[future]
                try:
                    page_text = future.result()
                    page_texts[page_index] = page_text
                    print(f"Completed page {page_index + 1}/{len(pages)}")
                except Exception as e:
                    print(f"Error processing page {page_index + 1}: {e}")
                    page_texts[page_index] = ""

        return "\n".join(page_texts)

    def _extract_single_page(self, page, page_num: int) -> str:
        """Extract text from a single page"""
        try:
            return page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from page {page_num + 1}: {e}")
            return ""

    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR (for image-based PDFs)"""
        if not self.ocr_available:
            raise Exception(
                "OCR libraries not installed. "
                "Run: pip install pytesseract pillow pdf2image"
            )

        try:
            import pytesseract
            from pdf2image import convert_from_path

            self._setup_tesseract()

            # Find Poppler path
            poppler_path = self._find_poppler_path()

            # Convert PDF to images
            if poppler_path:
                images = convert_from_path(pdf_path, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path)

            text = ""
            print(f"Converting {len(images)} pages to text using OCR...")

            # Use parallel processing for OCR
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit OCR tasks for each image
                futures = {
                    executor.submit(self._ocr_image, image, i + 1, len(images)): i
                    for i, image in enumerate(images)
                }

                # Collect results as they complete
                for future in as_completed(futures):
                    i = futures[future]
                    try:
                        page_text = future.result()
                        text += page_text + "\n"
                    except Exception as e:
                        print(f"Error processing page {i+1}: {str(e)}")

            return text.strip()

        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def _ocr_image(self, image, page_number: int, total_pages: int) -> str:
        """Perform OCR on a single image (page)"""
        import pytesseract

        print(f"Processing page {page_number}/{total_pages}...")
        return pytesseract.image_to_string(image)

    def _setup_tesseract(self) -> None:
        """Setup Tesseract OCR executable path"""
        import pytesseract

        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            (r"C:\Users\lshar\AppData\Local\Programs" r"\Tesseract-OCR\tesseract.exe"),
            r"C:\Program Files\tesseract\tesseract.exe",
        ]

        tesseract_found = False
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                tesseract_found = True
                print(f"Found Tesseract at: {path}")
                break

        if not tesseract_found:
            try:
                pytesseract.get_tesseract_version()
                tesseract_found = True
                print("Tesseract found in PATH")
            except Exception:
                pass

        if not tesseract_found:
            raise Exception(
                "Tesseract OCR not found. Please restart your terminal "
                "and try again, or install from: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )

    def _find_poppler_path(self) -> Optional[str]:
        """Find Poppler installation path"""
        base_path = (
            r"C:\Users\lshar\AppData\Local\Microsoft\WinGet"
            r"\Packages\oschwartz10612.Poppler_Microsoft."
            r"Winget.Source_8wekyb3d8bbwe\poppler-24.08.0"
            r"\Library\bin"
        )

        poppler_paths = [
            base_path,
            r"C:\Program Files\poppler\Library\bin",
            r"C:\Program Files (x86)\poppler\Library\bin",
            r"C:\poppler\Library\bin",
            r"C:\tools\poppler\Library\bin",
        ]

        for path in poppler_paths:
            if os.path.exists(os.path.join(path, "pdftoppm.exe")):
                print(f"Found Poppler at: {path}")
                return path

        return None

    def set_max_workers(self, max_workers: int) -> None:
        """Set the maximum number of worker threads for parallel processing"""
        self.max_workers = min(max_workers, 8)  # Cap at 8 for safety

    def get_max_workers(self) -> int:
        """Get the current maximum number of worker threads"""
        return self.max_workers


class TextCleaner:
    """Handles cleaning and formatting of extracted text."""

    @staticmethod
    def clean_email_text(text: str) -> str:
        """Clean and format email text"""
        # Remove excessive whitespace
        text = re.sub(r"\n\s*\n", "\n\n", text)

        # Remove page numbers and headers/footers
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines, page numbers, and common email artifacts
            if (
                line
                and not re.match(r"^\d+$", line)
                and not line.startswith("Page ")
                and len(line) > 3
            ):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
