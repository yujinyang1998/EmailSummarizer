import PyPDF2
from openai import OpenAI
import os
import re
from typing import Dict, List
from dotenv import load_dotenv

# OCR libraries for image-based PDFs
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

load_dotenv()


class PDFEmailSummarizer:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

                # If no text was extracted, try OCR
                if not text.strip() and OCR_AVAILABLE:
                    print("No text found with PyPDF2, trying OCR...")
                    text = self.extract_text_with_ocr(pdf_path)
                elif not text.strip():
                    return ""

                return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            # Try OCR as fallback
            if OCR_AVAILABLE:
                try:
                    print("Trying OCR as fallback...")
                    return self.extract_text_with_ocr(pdf_path)
                except Exception as ocr_e:
                    print(f"OCR also failed: {str(ocr_e)}")
            return ""

    def extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR (for image-based PDFs)"""
        if not OCR_AVAILABLE:
            raise Exception(
                "OCR libraries not installed. Run: pip install pytesseract pillow pdf2image"
            )

        try:
            # Import here to avoid issues if not installed
            import pytesseract
            from pdf2image import convert_from_path

            # Try to find Tesseract executable on Windows
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\lshar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
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
                # Try default (might be in PATH)
                try:
                    pytesseract.get_tesseract_version()
                    tesseract_found = True
                    print("Tesseract found in PATH")
                except Exception:
                    pass

            if not tesseract_found:
                raise Exception(
                    "Tesseract OCR not found. Please restart your terminal and try again, or install from: https://github.com/UB-Mannheim/tesseract/wiki"
                )  # Try to find Poppler (for pdf2image)
            poppler_paths = [
                r"C:\Users\lshar\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-24.08.0\Library\bin",
                r"C:\Program Files\poppler\Library\bin",
                r"C:\Program Files (x86)\poppler\Library\bin",
                r"C:\poppler\Library\bin",
                r"C:\tools\poppler\Library\bin",
            ]

            poppler_path = None
            for path in poppler_paths:
                if os.path.exists(os.path.join(path, "pdftoppm.exe")):
                    poppler_path = path
                    print(f"Found Poppler at: {path}")
                    break

            # Convert PDF to images with poppler path if needed
            if poppler_path:
                images = convert_from_path(pdf_path, poppler_path=poppler_path)
            else:
                # Try without explicit path (might be in PATH after restart)
                images = convert_from_path(pdf_path)

            text = ""
            print(f"Converting {len(images)} pages to text using OCR...")

            for i, image in enumerate(images):
                print(f"Processing page {i+1}/{len(images)}...")
                # Extract text from image using OCR
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"

            return text.strip()

        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def clean_email_text(self, text: str) -> str:
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

    def extract_email_info(self, text: str) -> Dict:
        """Extract basic email information from text"""
        email_info = {
            "subject": "Not found",
            "from": "Not found",
            "to": "Not found",
            "date": "Not found",
            "content": text,
        }

        lines = text.split("\n")

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Extract subject
            if "subject:" in line_lower:
                email_info["subject"] = line.split(":", 1)[1].strip()

            # Extract from
            elif "from:" in line_lower:
                email_info["from"] = line.split(":", 1)[1].strip()

            # Extract to
            elif "to:" in line_lower:
                email_info["to"] = line.split(":", 1)[1].strip()

            # Extract date
            elif any(word in line_lower for word in ["date:", "sent:", "received:"]):
                email_info["date"] = line.split(":", 1)[1].strip()

        return email_info

    def split_email_threads(self, text: str) -> List[Dict]:
        """Split text into individual email threads"""
        # Look for common email separators
        separators = [
            r"From:.*?@.*",
            r"-----Original Message-----",
            r"________________________________",
            r"On .* wrote:",
            r"Begin forwarded message:",
        ]

        emails = []
        current_email = text

        # Try to split by common patterns
        for separator in separators:
            parts = re.split(separator, current_email, flags=re.IGNORECASE)
            if len(parts) > 1:
                emails = []
                for i, part in enumerate(parts):
                    if part.strip():
                        # Add separator back to maintain context
                        if i > 0:
                            match = re.search(separator, current_email, re.IGNORECASE)
                            if match:
                                part = match.group(0) + part
                        emails.append(self.extract_email_info(part.strip()))
                break

        # If no separators found, treat as single email
        if not emails:
            emails = [self.extract_email_info(text)]

        return emails

    def generate_summary_prompt(
        self, emails: List[Dict], summary_type: str = "medium"
    ) -> str:
        """Generate prompt for AI summarization"""

        if summary_type == "short":
            prompt = """
Please provide a brief 2-3 sentence summary of this email thread focusing on the main topic and key outcomes.

Email Thread:
"""
        elif summary_type == "long":
            prompt = """
Please provide a detailed summary of this email thread including:
1. Main topic and background
2. Key participants and their roles
3. Important points discussed
4. Decisions made or action items
5. Timeline of events

Email Thread:
"""
        else:  # medium
            prompt = """
Please provide a comprehensive summary of this email thread including:
1. Main topic and context
2. Key participants
3. Important decisions or action items
4. Outcomes

Email Thread:
"""

        # Add email content to prompt
        for i, email in enumerate(emails):
            prompt += f"\n--- Email {i+1} ---\n"
            prompt += f"From: {email['from']}\n"
            prompt += f"To: {email['to']}\n"
            prompt += f"Subject: {email['subject']}\n"
            prompt += f"Date: {email['date']}\n"
            prompt += f"Content: {email['content'][:1000]}...\n"  # Limit content

        return prompt

    def summarize_with_openai(
        self, emails: List[Dict], summary_type: str = "medium"
    ) -> str:
        """Generate summary using OpenAI"""
        try:
            if not self.openai_client:
                return self.generate_basic_summary(emails)

            prompt = self.generate_summary_prompt(emails, summary_type)

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes email content clearly and concisely.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500 if summary_type == "short" else 1000,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return self.generate_basic_summary(emails)

    def generate_basic_summary(self, emails: List[Dict]) -> str:
        """Generate basic summary without AI"""

        summary_parts = []

        # Thread overview
        summary_parts.append("**Email Thread Summary**")
        summary_parts.append(f"**Number of emails:** {len(emails)}")

        if len(emails) > 0:
            first_email = emails[0]
            summary_parts.append(f"**Subject:** {first_email['subject']}")
            summary_parts.append(
                f"**Main participants:** {first_email['from']} → {first_email['to']}"
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
                summary_parts.append(
                    f"**All participants:** {', '.join(list(participants)[:5])}"
                )

        return "\n\n".join(summary_parts)

    def summarize_pdf_emails(
        self, pdf_path: str = "email.pdf", summary_type: str = "medium"
    ) -> Dict:
        """Main method to summarize emails from PDF"""
        try:  # Extract text from PDF
            raw_text = self.extract_text_from_pdf(pdf_path)
            if not raw_text:
                return {
                    "error": "Could not extract text from PDF. This appears to be an image-based PDF (scanned document). To process this type of PDF, you would need to:\n\n1. Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki\n2. Install Poppler: Download from https://github.com/oschwartz10612/poppler-windows/releases/\n3. Add both to your system PATH\n\nAlternatively, try converting your PDF to a text-based PDF using online tools or save your emails as text instead of scanning them."
                }

            # Clean the text
            clean_text = self.clean_email_text(raw_text)

            # Split into email threads
            emails = self.split_email_threads(clean_text)

            # Generate summary
            if self.openai_api_key and len(clean_text) > 100:
                summary = self.summarize_with_openai(emails, summary_type)
            else:
                summary = self.generate_basic_summary(emails)

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


def main():
    """Simple command line interface"""
    summarizer = PDFEmailSummarizer()

    print("PDF Email Summarizer")
    print("===================")

    # Check if email.pdf exists
    pdf_path = "email.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found in current directory")
        return

    print(f"Processing {pdf_path}...")

    # Ask for summary type
    print("\nChoose summary type:")
    print("1. Short (2-3 sentences)")
    print("2. Medium (comprehensive)")
    print("3. Long (detailed analysis)")

    choice = input("Enter choice (1-3) or press Enter for medium: ").strip()

    summary_types = {"1": "short", "2": "medium", "3": "long"}
    summary_type = summary_types.get(choice, "medium")

    # Generate summary
    result = summarizer.summarize_pdf_emails(pdf_path, summary_type)

    if "error" in result:
        print(f"\nError: {result['error']}")
        return

    # Display results
    print(f"\n{'='*50}")
    print(f"SUMMARY ({summary_type.upper()})")
    print(f"{'='*50}")
    print(f"Emails found: {result['email_count']}")
    print(f"Text length: {result['raw_text_length']} characters")
    print(f"\n{result['summary']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
