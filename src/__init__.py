"""
PDF Email Summarizer Package

A tool for extracting and summarizing email content from PDF files.
"""

from .pdf_email_summarizer import PDFEmailSummarizer
from .text_extractor import PDFTextExtractor, TextCleaner
from .email_parser import EmailParser

try:
    from .ai_summarizer import AISummarizer
except ImportError:
    # AI summarizer dependencies not available
    AISummarizer = None

__version__ = "1.0.0"
__all__ = [
    "PDFEmailSummarizer",
    "PDFTextExtractor",
    "TextCleaner",
    "EmailParser",
    "AISummarizer",
]
