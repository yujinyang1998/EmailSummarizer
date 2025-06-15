"""
Email file processor for handling .eml, .msg, and attachment extraction.
"""

import os
import email
import tempfile
from email.header import decode_header
from pathlib import Path
from typing import Dict, List, Optional, Union
from .native_msg_parser import parse_msg_file_native

try:
    import extract_msg

    EXTRACT_MSG_AVAILABLE = True
except ImportError:
    EXTRACT_MSG_AVAILABLE = False

# MSG support is now always available through native parser
MSG_SUPPORT = True


class EmailFileProcessor:
    """Handles processing of .eml and .msg email files with attachments."""

    def __init__(self):
        # MSG support is now always available
        self.supported_formats = [".eml", ".pdf", ".msg"]

        # Supported attachment types for content extraction
        self.extractable_attachments = [
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
            ".rtf",
            ".html",
            ".htm",
        ]

    def is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """Check if the file format is supported."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats

    def process_email_file(self, file_path: Union[str, Path]) -> Dict:
        """
        Process an email file (.eml or .msg) and extract content and attachments.

        Returns:
            Dict containing email metadata, content, and attachment information
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        file_ext = file_path.suffix.lower()

        try:
            if file_ext == ".eml":
                return self._process_eml_file(file_path)
            elif file_ext == ".msg" and MSG_SUPPORT:
                return self._process_msg_file(file_path)
            elif file_ext == ".pdf":
                # Fallback to PDF processing
                return {"error": "PDF processing should be handled by PDF processor"}
            else:
                return {"error": f"Unsupported file format: {file_ext}"}

        except Exception as e:
            return {"error": f"Failed to process email file: {str(e)}"}

    def _process_eml_file(self, file_path: Path) -> Dict:
        """Process .eml email file."""
        try:
            with open(file_path, "rb") as f:
                msg = email.message_from_bytes(f.read())

            # Extract basic email metadata
            from_addr = self._decode_header(msg.get("From", ""))
            to_addr = self._decode_header(msg.get("To", ""))

            email_data = {
                "format": "eml",
                "file_path": str(file_path),
                "subject": self._decode_header(msg.get("Subject", "")),
                "from": from_addr,
                "sender": from_addr,  # For compatibility
                "to": to_addr,
                "recipient": to_addr,  # For compatibility
                "cc": self._decode_header(msg.get("Cc", "")),
                "date": msg.get("Date", ""),
                "message_id": msg.get("Message-ID", ""),
                "content": "",
                "attachments": [],
                "attachment_contents": {},
            }

            # Extract email content and attachments
            content_parts = []
            attachments = []

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if part.is_multipart():
                    continue

                if "attachment" in content_disposition:
                    # Handle attachment
                    attachment_info = self._process_attachment(part)
                    if attachment_info:
                        attachments.append(attachment_info)

                        # Extract text from attachment if possible
                        if attachment_info.get("extracted_text"):
                            email_data["attachment_contents"][
                                attachment_info["filename"]
                            ] = attachment_info["extracted_text"]

                elif content_type == "text/plain":
                    # Plain text content
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            if isinstance(payload, bytes):
                                text = payload.decode("utf-8", errors="ignore")
                            else:
                                text = str(payload)
                            content_parts.append(text)
                    except Exception as e:
                        content_parts.append(f"[Error decoding text: {e}]")

                elif content_type == "text/html":
                    # HTML content - convert to text
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            if isinstance(payload, bytes):
                                html = payload.decode("utf-8", errors="ignore")
                            else:
                                html = str(payload)
                            # Simple HTML to text conversion
                            text = self._html_to_text(html)
                            content_parts.append(text)
                    except Exception as e:
                        content_parts.append(f"[Error decoding HTML: {e}]")

            email_data["content"] = "\n\n".join(content_parts)
            email_data["attachments"] = attachments

            return email_data

        except Exception as e:
            return {"error": f"Failed to process .eml file: {str(e)}"}

    def _process_msg_file(self, file_path: Path) -> Dict:
        """Process .msg email file using native parser with extract_msg fallback."""

        # Try native parser first
        try:
            result = parse_msg_file_native(file_path)

            # If native parser succeeded, return the result
            if "error" not in result:
                return result

            # If native parser failed but extract_msg is available, try it
            if EXTRACT_MSG_AVAILABLE:
                return self._process_msg_with_extract_msg(file_path)
            else:
                # Return the native parser result (which contains the error)
                return result

        except Exception as e:
            # If native parser threw an exception, try extract_msg if available
            if EXTRACT_MSG_AVAILABLE:
                try:
                    return self._process_msg_with_extract_msg(file_path)
                except Exception:
                    pass

            return {"error": f"Failed to process .msg file: {str(e)}"}

    def _process_msg_with_extract_msg(self, file_path: Path) -> Dict:
        """Process .msg file using the extract_msg library."""
        try:
            msg = extract_msg.Message(str(file_path))

            sender = msg.sender or ""
            recipient = msg.to or ""

            email_data = {
                "format": "msg",
                "file_path": str(file_path),
                "subject": msg.subject or "",
                "from": sender,
                "sender": sender,  # For compatibility
                "to": recipient,
                "recipient": recipient,  # For compatibility
                "cc": msg.cc or "",
                "date": str(msg.date) if msg.date else "",
                "message_id": msg.messageId or "",
                "content": msg.body or "",
                "attachments": [],
                "attachment_contents": {},
            }

            # Process attachments
            attachments = []
            for attachment in msg.attachments:
                attachment_info = self._process_msg_attachment(attachment)
                if attachment_info:
                    attachments.append(attachment_info)

                    # Extract text from attachment if possible
                    if attachment_info.get("extracted_text"):
                        email_data["attachment_contents"][
                            attachment_info["filename"]
                        ] = attachment_info["extracted_text"]

            email_data["attachments"] = attachments
            msg.close()

            return email_data

        except Exception as e:
            return {"error": f"Failed to process .msg file: {str(e)}"}

    def _process_attachment(self, part) -> Optional[Dict]:
        """Process an attachment from an email part."""
        try:
            filename = part.get_filename()
            if not filename:
                return None

            # Decode filename if necessary
            filename = self._decode_header(filename)

            attachment_info = {
                "filename": filename,
                "content_type": part.get_content_type(),
                "size": 0,
                "extracted_text": None,
            }

            # Get attachment content
            payload = part.get_payload(decode=True)
            if payload:
                attachment_info["size"] = len(payload)

                # Try to extract text from certain file types
                file_ext = Path(filename).suffix.lower()
                if file_ext in self.extractable_attachments:
                    extracted_text = self._extract_text_from_attachment(
                        payload, filename, part.get_content_type()
                    )
                    if extracted_text:
                        attachment_info["extracted_text"] = extracted_text

            return attachment_info

        except Exception as e:
            return {
                "filename": "unknown_attachment",
                "content_type": "unknown",
                "size": 0,
                "error": str(e),
            }

    def _process_msg_attachment(self, attachment) -> Optional[Dict]:
        """Process an attachment from a .msg file."""
        try:
            filename = attachment.longFilename or attachment.shortFilename or "unknown"

            attachment_info = {
                "filename": filename,
                "content_type": "application/octet-stream",
                "size": len(attachment.data) if attachment.data else 0,
                "extracted_text": None,
            }

            # Try to extract text from certain file types
            if attachment.data:
                file_ext = Path(filename).suffix.lower()
                if file_ext in self.extractable_attachments:
                    extracted_text = self._extract_text_from_attachment(
                        attachment.data, filename, attachment_info["content_type"]
                    )
                    if extracted_text:
                        attachment_info["extracted_text"] = extracted_text

            return attachment_info

        except Exception as e:
            return {
                "filename": "unknown_attachment",
                "content_type": "unknown",
                "size": 0,
                "error": str(e),
            }

    def _extract_text_from_attachment(
        self, data: bytes, filename: str, content_type: str
    ) -> Optional[str]:
        """Extract text content from attachment data."""
        file_ext = Path(filename).suffix.lower()

        try:
            if file_ext == ".txt":
                return data.decode("utf-8", errors="ignore")

            elif file_ext == ".html" or file_ext == ".htm":
                html_content = data.decode("utf-8", errors="ignore")
                return self._html_to_text(html_content)

            elif file_ext == ".pdf":
                # Save to temp file and process with PDF extractor
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(data)
                    tmp_path = tmp.name

                try:
                    # Import here to avoid circular imports
                    from .text_extractor import PDFTextExtractor

                    extractor = PDFTextExtractor()
                    text = extractor.extract_text_from_pdf(tmp_path)
                    return text
                finally:
                    os.unlink(tmp_path)

            # For other formats, we could add more processors here
            # (.doc, .docx, etc.) but that would require additional dependencies

            return None

        except Exception as e:
            return f"[Error extracting text from {filename}: {e}]"

    def _decode_header(self, header_value: str) -> str:
        """Decode email header that might be encoded."""
        if not header_value:
            return ""

        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ""

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding, errors="ignore")
                    else:
                        decoded_string += part.decode("utf-8", errors="ignore")
                else:
                    decoded_string += str(part)

            return decoded_string.strip()

        except Exception:
            # If decoding fails, return the original string
            return str(header_value)

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text."""
        try:
            # Try using markdownify for better HTML to text conversion
            from markdownify import markdownify

            text = markdownify(html_content, heading_style="ATX")
            return text.strip()
        except ImportError:
            # Fallback: simple tag removal
            import re

            # Remove HTML tags
            text = re.sub(r"<[^>]+>", "", html_content)
            # Clean up whitespace
            text = re.sub(r"\s+", " ", text)
            return text.strip()

    def get_supported_formats(self) -> List[str]:
        """Get list of currently supported file formats."""
        return self.supported_formats.copy()

    def check_dependencies(self) -> Dict[str, bool]:
        """Check which optional dependencies are available."""
        return {
            "msg_support": True,  # Native MSG parser always available
            "extract_msg": EXTRACT_MSG_AVAILABLE,  # Optional enhanced MSG support
            "eml_support": True,  # Built-in email module
            "pdf_fallback": True,  # PDF processing handled elsewhere
        }

    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependencies for enhanced functionality."""
        missing = []
        if not EXTRACT_MSG_AVAILABLE:
            missing.append("extract-msg (for enhanced .msg file support - optional)")
        return missing

    def extract_emails_from_file(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Extract emails from a file and return them in a standardized format.

        This method provides compatibility with the existing email parser interface.
        """
        result = self.process_email_file(file_path)

        if "error" in result:
            return []

        # Convert to the format expected by the existing system
        email_entry = {
            "subject": result.get("subject", ""),
            "sender": result.get("sender", result.get("from", "")),
            "from": result.get("from", ""),
            "recipient": result.get("recipient", result.get("to", "")),
            "to": result.get("to", ""),
            "date": result.get("date", ""),
            "content": result.get("content", ""),
            "message_id": result.get("message_id", ""),
        }

        # Add attachment content to the main content
        attachment_texts = []
        for filename, content in result.get("attachment_contents", {}).items():
            if content:
                attachment_texts.append(f"\n--- Attachment: {filename} ---\n{content}")

        if attachment_texts:
            email_entry["content"] += "\n\n" + "\n".join(attachment_texts)

        return [email_entry]
