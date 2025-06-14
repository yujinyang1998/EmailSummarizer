"""
Main PDF Email Summarizer class that orchestrates all components.
"""

from typing import Dict, List, Optional
from .text_extractor import PDFTextExtractor, TextCleaner
from .email_parser import EmailParser


class PDFEmailSummarizer:
    """Main class that orchestrates PDF email summarization."""

    def __init__(self, max_workers: Optional[int] = None):
        self.text_extractor = PDFTextExtractor(max_workers=max_workers)
        self.text_cleaner = TextCleaner()
        self.email_parser = EmailParser()
        self.ai_summarizer = None

        # Try to import AI summarizer if available
        try:
            from .ai_summarizer import AISummarizer

            self.ai_summarizer = AISummarizer()
        except ImportError:
            print("AI summarizer not available, using basic summarization")

    def set_parallel_workers(self, max_workers: int) -> None:
        """Configure the number of parallel workers for processing"""
        self.text_extractor.set_max_workers(max_workers)

    def get_parallel_workers(self) -> int:
        """Get the current number of parallel workers"""
        return self.text_extractor.get_max_workers()

    def summarize_pdf_emails(
        self, pdf_path: str = "email.pdf", summary_type: str = "medium"
    ) -> Dict:
        """Main method to summarize emails from PDF"""
        try:
            # Extract text from PDF
            raw_text = self.text_extractor.extract_text_from_pdf(pdf_path)
            if not raw_text:
                return {
                    "error": (
                        "Could not extract text from PDF. This appears to be "
                        "an image-based PDF (scanned document). To process "
                        "this type of PDF, you would need to:\n\n"
                        "1. Install Tesseract OCR: "
                        "https://github.com/UB-Mannheim/tesseract/wiki\n"
                        "2. Install Poppler: Download from "
                        "https://github.com/oschwartz10612/poppler-windows/"
                        "releases/\n"
                        "3. Add both to your system PATH\n\n"
                        "Alternatively, try converting your PDF to a "
                        "text-based PDF using online tools or save your "
                        "emails as text instead of scanning them."
                    )
                }  # Clean the text
            clean_text = self.text_cleaner.clean_email_text(raw_text)

            # Split into email threads
            emails = self.email_parser.split_email_threads(clean_text)

            # Generate summary
            if (
                self.ai_summarizer
                and self.ai_summarizer.openai_client
                and len(clean_text) > 100
            ):
                summary = self.ai_summarizer.summarize_with_openai(emails, summary_type)
            else:
                summary = self._generate_basic_summary(emails)

            return {
                "success": True,
                "email_count": len(emails),
                "summary": summary,
                "summary_type": summary_type,
                "raw_text_length": len(raw_text),
                "emails": emails,
            }

        except Exception as e:
            return {"error": f"Error processing PDF: {str(e)}"}

    def _generate_basic_summary(self, emails: List[Dict]) -> str:
        """Generate basic summary without AI"""
        summary_parts = []

        # Thread overview
        summary_parts.append("**Email Thread Summary**")
        summary_parts.append(f"**Number of emails:** {len(emails)}")

        if len(emails) > 0:
            first_email = emails[0]
            summary_parts.append(f"**Subject:** {first_email['subject']}")
            summary_parts.append(
                f"**Main participants:** {first_email['from']} → "
                f"{first_email['to']}"
            )

            # Content preview
            content_preview = first_email["content"][:300]
            summary_parts.append(f"**Content preview:** {content_preview}...")

        if len(emails) > 1:
            summary_parts.append(f"\n**Thread contains {len(emails)} related emails**")

            # Show unique participants
            participants = set()
            for email in emails:
                if email["from"] != "Not found":
                    participants.add(email["from"])

            if participants:
                participant_list = ", ".join(list(participants)[:5])
                summary_parts.append(f"**All participants:** {participant_list}")

        return "\n\n".join(summary_parts)
