"""
Backward compatibility module for the original email_summarizer.py
This module imports and exposes the refactored classes.
"""

from .pdf_email_summarizer import PDFEmailSummarizer
from .cli import main

# For backward compatibility, expose the main class with the original name
PDFEmailSummarizer = PDFEmailSummarizer


if __name__ == "__main__":
    main()
