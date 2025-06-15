"""
Main Email Summarizer class that orchestrates all components.
Supports PDF, EML, and MSG file formats.
"""

from pathlib import Path
from typing import Dict, List, Optional
from ..processors.text_extractor import PDFTextExtractor, TextCleaner
from ..processors.email_parser import EmailParser
from ..processors.email_file_processor import EmailFileProcessor


class PDFEmailSummarizer:
    """Main class that orchestrates email summarization from various formats."""

    def __init__(self, max_workers: Optional[int] = None):
        self.text_extractor = PDFTextExtractor(max_workers=max_workers)
        self.text_cleaner = TextCleaner()
        self.email_parser = EmailParser()
        self.email_file_processor = EmailFileProcessor()
        self.ai_summarizer = None  # Try to import AI summarizer if available
        try:
            from ..ai.ai_summarizer import AISummarizer

            self.ai_summarizer = AISummarizer()
        except ImportError:
            print("AI summarizer not available, using basic summarization")

    def set_parallel_workers(self, max_workers: int) -> None:
        """Configure the number of parallel workers for processing"""
        self.text_extractor.set_max_workers(max_workers)

    def get_parallel_workers(self) -> int:
        """Get the current number of parallel workers"""
        return self.text_extractor.get_max_workers()

    def summarize_emails_from_file(
        self,
        file_path: str = "email.pdf",
        summary_type: str = "medium",
        api_key: Optional[str] = None,
    ) -> Dict:
        """Main method to summarize emails from various file formats (.pdf, .eml, .msg)"""
        try:
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()

            # Route to appropriate processor based on file extension
            if file_extension == ".pdf":
                return self._process_pdf_file(file_path, summary_type, api_key)
            elif file_extension in [".eml", ".msg"]:
                return self._process_email_file(file_path, summary_type, api_key)
            else:
                return {
                    "error": f"Unsupported file format: {file_extension}. Supported formats: .pdf, .eml, .msg"
                }

        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}

    def summarize_pdf_emails(
        self,
        pdf_path: str = "email.pdf",
        summary_type: str = "medium",
        api_key: Optional[str] = None,
    ) -> Dict:
        """Backward compatibility method - routes to the new unified method"""
        return self.summarize_emails_from_file(pdf_path, summary_type, api_key)

    def _process_pdf_file(
        self,
        pdf_path: str,
        summary_type: str = "medium",
        api_key: Optional[str] = None,
    ) -> Dict:
        """Process PDF email file"""
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
                }

            # Clean the text
            clean_text = self.text_cleaner.clean_email_text(raw_text)

            # Split into email threads
            emails = self.email_parser.split_email_threads(clean_text)

            # Generate summary
            return self._generate_summary(emails, clean_text, summary_type, api_key)

        except Exception as e:
            return {"error": f"Error processing PDF: {str(e)}"}

    def _process_email_file(
        self,
        file_path: str,
        summary_type: str = "medium",
        api_key: Optional[str] = None,
    ) -> Dict:
        """Process .eml or .msg email file"""
        try:
            # Use EmailFileProcessor to extract email data
            email_data = self.email_file_processor.process_email_file(file_path)

            if "error" in email_data:
                return email_data

            # Convert to the format expected by the existing system
            emails = self.email_file_processor.extract_emails_from_file(file_path)

            if not emails:
                return {"error": "No emails found in the file"}

            # Prepare content for summary generation
            content_parts = []
            for email in emails:
                content_parts.append(email["content"])

            clean_text = "\n\n".join(content_parts)

            # Generate summary
            result = self._generate_summary(emails, clean_text, summary_type, api_key)

            # Add file format information
            result["file_format"] = email_data.get("format", "unknown")
            result["attachments_count"] = len(email_data.get("attachments", []))

            return result

        except Exception as e:
            return {"error": f"Error processing email file: {str(e)}"}

    def _generate_summary(
        self,
        emails: List[Dict],
        clean_text: str,
        summary_type: str,
        api_key: Optional[str] = None,
    ) -> Dict:
        """Generate summary from emails using AI or basic summarization"""
        try:
            ai_summarizer_to_use = (
                self.ai_summarizer
            )  # If API key is provided, create a new AI summarizer instance
            if api_key:
                try:
                    from ..ai.ai_summarizer import AISummarizer

                    ai_summarizer_to_use = AISummarizer(api_key=api_key)
                except ImportError:
                    pass  # Fall back to default summarizer or basic summary

            if (
                ai_summarizer_to_use
                and ai_summarizer_to_use.openai_client
                and len(clean_text) > 100
            ):
                summary = ai_summarizer_to_use.summarize_with_openai(
                    emails, summary_type
                )
            else:
                summary = self._generate_basic_summary(emails)

            return {
                "success": True,
                "email_count": len(emails),
                "summary": summary,
                "summary_type": summary_type,
                "raw_text_length": len(clean_text),
                "emails": emails,
            }
        except Exception as e:
            return {"error": f"Error generating summary: {str(e)}"}

    def _generate_basic_summary(self, emails: List[Dict]) -> str:
        """Generate enhanced basic summary without AI"""
        summary_parts = []

        # Thread overview
        summary_parts.append("**📧 Email Thread Summary**")
        summary_parts.append(f"**Number of emails:** {len(emails)}")

        if len(emails) > 0:
            first_email = emails[0]
            summary_parts.append(f"**Subject:** {first_email['subject']}")
            summary_parts.append(
                f"**Main participants:** **{first_email.get('sender', first_email.get('from', 'Unknown'))}** → "
                f"**{first_email.get('recipient', first_email.get('to', 'Unknown'))}**"
            )

            # Enhanced content analysis
            content = first_email["content"]

            # Look for important patterns
            important_details = []

            # Search for dates, deadlines, amounts, etc.
            import re

            # Find dates
            date_patterns = [
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
            ]

            for pattern in date_patterns:
                dates = re.findall(pattern, content, re.IGNORECASE)
                for date in dates[:3]:  # Limit to 3 dates
                    important_details.append(f"**Date:** {date}")

            # Find dollar amounts
            money_pattern = r"\$[\d,]+(?:\.\d{2})?"
            amounts = re.findall(money_pattern, content)
            for amount in amounts[:3]:  # Limit to 3 amounts
                important_details.append(f"**Amount:** {amount}")

            # Find action words that might indicate important items
            action_patterns = [
                r"(?:deadline|due|complete|finish|deliver|submit|send|review|approve|sign|meet|call|discuss|decide)[^.]*",
                r"(?:urgent|important|priority|asap|immediately|critical)[^.]*",
                r"(?:action item|to do|task|assignment|responsibility)[^.]*",
            ]

            for pattern in action_patterns:
                actions = re.findall(pattern, content, re.IGNORECASE)
                for action in actions[:2]:  # Limit to 2 per pattern
                    important_details.append(f"**Action:** {action[:100]}...")

            # Content preview
            content_preview = content[:300]
            summary_parts.append(f"**Content preview:** {content_preview}...")

            # Add important details if found
            if important_details:
                summary_parts.append("**🔍 Important Details Found:**")
                summary_parts.extend(important_details[:5])  # Limit to 5 total details

        if len(emails) > 1:
            summary_parts.append(
                f"\n**📊 Thread contains {len(emails)} related emails**"
            )

            # Show unique participants
            participants = set()
            subjects = set()
            all_content = ""

            for email in emails:
                sender = email.get("sender", email.get("from"))
                if sender and sender != "Not found":
                    participants.add(sender)

                subject = email.get("subject", "")
                if subject:
                    subjects.add(subject)

                all_content += " " + email.get("content", "")

            if participants:
                participant_list = ", ".join(
                    [f"**{p}**" for p in list(participants)[:5]]
                )
                summary_parts.append(f"**All participants:** {participant_list}")

            # Check for recurring subjects/topics
            if len(subjects) > 1:
                summary_parts.append(
                    f"**Topic evolution:** {len(subjects)} different subjects discussed"
                )

            # Search for important details across all emails
            thread_details = []

            # Find patterns across the thread
            import re

            deadline_pattern = r"(?:deadline|due|by|before)[^.]*(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b)"
            deadlines = re.findall(deadline_pattern, all_content, re.IGNORECASE)
            for deadline in deadlines[:2]:
                thread_details.append(f"**⏰ Deadline:** {deadline[:80]}...")

            decision_pattern = (
                r"(?:decided|agreed|concluded|determined|approved|rejected)[^.]*"
            )
            decisions = re.findall(decision_pattern, all_content, re.IGNORECASE)
            for decision in decisions[:2]:
                thread_details.append(f"**✅ Decision:** {decision[:80]}...")

            if thread_details:
                summary_parts.append("**🎯 Key Thread Highlights:**")
                summary_parts.extend(thread_details)

        return "\n\n".join(summary_parts)
