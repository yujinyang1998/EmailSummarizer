"""
EmailSummarizer Package

A tool for extracting and summarizing email content from PDF, EML, and MSG files.
"""

from .core.pdf_email_summarizer import PDFEmailSummarizer
from .processors.text_extractor import PDFTextExtractor, TextCleaner
from .processors.email_parser import EmailParser
from .processors.email_file_processor import EmailFileProcessor

try:
    from .ai.ai_summarizer import AISummarizer
except ImportError:
    # AI summarizer dependencies not available
    AISummarizer = None

__version__ = "2.0.0"
__all__ = [
    "PDFEmailSummarizer",
    "PDFTextExtractor",
    "TextCleaner",
    "EmailParser",
    "EmailFileProcessor",
    "AISummarizer",
]
