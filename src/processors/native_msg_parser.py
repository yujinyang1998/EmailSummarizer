"""
Native MSG file parser implementation.
Handles Microsoft Outlook .msg files without external dependencies.
"""

import struct
import io
from typing import Dict, List, Optional, Union, BinaryIO
from pathlib import Path


class NativeMsgParser:
    """Native Python implementation for parsing .msg files."""

    # MSG file format constants
    MSG_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

    # Common property tags for email data
    PROPERTY_TAGS = {
        0x0037001F: "subject",  # PR_SUBJECT
        0x0C1A001F: "sender_name",  # PR_SENDER_NAME
        0x0C1F001F: "sender_email",  # PR_SENDER_EMAIL_ADDRESS
        0x0E03001F: "display_to",  # PR_DISPLAY_TO
        0x0E04001F: "display_cc",  # PR_DISPLAY_CC
        0x1000001F: "body",  # PR_BODY
        0x10130102: "html_body",  # PR_HTML
        0x0039001F: "client_submit_time",  # PR_CLIENT_SUBMIT_TIME
        0x007D001F: "transport_headers",  # PR_TRANSPORT_MESSAGE_HEADERS
    }

    def __init__(self):
        self.is_valid_msg = False
        self.email_data = {}

    def parse_msg_file(self, file_path: Union[str, Path]) -> Dict:
        """
        Parse a .msg file and extract email data.

        Returns:
            Dict containing email data or error information
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            with open(file_path, "rb") as f:
                return self._parse_msg_stream(f, file_path)
        except Exception as e:
            return {"error": f"Failed to parse MSG file: {str(e)}"}

    def _parse_msg_stream(self, stream: BinaryIO, file_path: Path) -> Dict:
        """Parse MSG file from a binary stream."""

        # Check MSG file signature
        signature = stream.read(8)
        if signature != self.MSG_SIGNATURE:
            return self._fallback_text_extraction(file_path)

        # Reset to beginning for full parsing
        stream.seek(0)

        try:
            # Attempt to parse the compound document structure
            email_data = self._parse_compound_document(stream)

            if not email_data or not any(email_data.values()):
                # If structured parsing fails, try text extraction
                return self._fallback_text_extraction(file_path)

            # Attempt to detect attachments from the binary content
            try:
                stream.seek(0)
                full_content = stream.read()
                attachments, attachment_contents = self._detect_attachments(
                    full_content, email_data
                )
            except Exception:
                attachments, attachment_contents = [], {}

            return {
                "format": "msg",
                "file_path": str(file_path),
                "subject": email_data.get("subject", ""),
                "from": email_data.get("sender_email", ""),
                "sender": email_data.get("sender_email", ""),
                "sender_name": email_data.get("sender_name", ""),
                "to": email_data.get("display_to", ""),
                "recipient": email_data.get("display_to", ""),
                "cc": email_data.get("display_cc", ""),
                "date": email_data.get("client_submit_time", ""),
                "content": self._get_best_content(email_data),
                "attachments": attachments,
                "attachment_contents": attachment_contents,
                "native_parser": True,
            }

        except Exception as e:
            # If all else fails, try text extraction
            return self._fallback_text_extraction(file_path)

    def _parse_compound_document(self, stream: BinaryIO) -> Dict:
        """Parse the compound document structure of MSG file."""
        email_data = {}

        try:
            # Read the header
            stream.seek(0)
            header = stream.read(512)

            if len(header) < 512:
                return {}

            # Extract basic directory information
            # This is a simplified approach - full CFB parsing is complex

            # Try to find text content using simple heuristics
            stream.seek(0)
            content = stream.read()

            # Look for common email patterns in the binary data
            email_data = self._extract_text_patterns(content)

        except Exception:
            pass

        return email_data

    def _extract_text_patterns(self, content: bytes) -> Dict:
        """Extract email data using text pattern matching."""
        email_data = {}

        try:
            # Convert to text, ignoring errors
            text_content = content.decode("utf-8", errors="ignore")

            # Also try with latin-1 encoding
            if not text_content.strip():
                text_content = content.decode("latin-1", errors="ignore")

            # Extract subject using common patterns
            subject_patterns = [
                r"Subject:\s*(.+?)[\r\n]",
                r"Subject[:\s]+([^\r\n]+)",
            ]

            for pattern in subject_patterns:
                import re

                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    email_data["subject"] = match.group(1).strip()
                    break

            # Extract sender information
            from_patterns = [
                r"From:\s*([^\r\n]+)",
                r"Sender:\s*([^\r\n]+)",
                r"<([^@]+@[^>]+)>",
            ]

            for pattern in from_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    sender_info = match.group(1).strip()
                    if "@" in sender_info:
                        email_data["sender_email"] = sender_info
                    else:
                        email_data["sender_name"] = sender_info
                    break

            # Extract To information
            to_patterns = [
                r"To:\s*([^\r\n]+)",
                r"Recipients?:\s*([^\r\n]+)",
            ]

            for pattern in to_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    email_data["display_to"] = match.group(1).strip()
                    break

            # Extract body content - look for main text
            # Find the largest block of readable text
            lines = text_content.split("\n")
            content_lines = []

            for line in lines:
                # Skip lines that look like headers or metadata
                line = line.strip()
                if (
                    len(line) > 20
                    and not line.startswith(
                        ("From:", "To:", "Subject:", "Date:", "Message-ID:")
                    )
                    and not re.match(r"^[A-F0-9\s]+$", line)  # Skip hex dumps
                    and len([c for c in line if c.isalpha()]) > len(line) * 0.5
                ):  # Must be mostly letters
                    content_lines.append(line)

            if content_lines:
                # Take the longest contiguous block
                email_data["body"] = "\n".join(
                    content_lines[:50]
                )  # Limit to first 50 lines

        except Exception:
            pass

        return email_data

    def _get_best_content(self, email_data: Dict) -> str:
        """Get the best available content from parsed data."""
        # Prefer HTML body, then plain text body
        if email_data.get("html_body"):
            return self._html_to_text(email_data["html_body"])
        elif email_data.get("body"):
            return email_data["body"]
        else:
            return ""

    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion."""
        import re

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)

        # Decode HTML entities
        replacements = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&nbsp;": " ",
        }

        for entity, char in replacements.items():
            text = text.replace(entity, char)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def _fallback_text_extraction(self, file_path: Path) -> Dict:
        """Fallback method using simple text extraction."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Try different encodings
            text_content = ""
            for encoding in ["utf-8", "latin-1", "cp1252", "utf-16"]:
                try:
                    text_content = content.decode(encoding, errors="ignore")
                    if text_content.strip():
                        break
                except:
                    continue

            if not text_content.strip():
                return {"error": "Could not extract readable text from MSG file"}

            # Extract basic email information using simple patterns
            email_data = self._extract_text_patterns(content)

            # If we didn't find much, provide basic info
            if not email_data.get("subject") and not email_data.get("body"):
                # Find the first line that looks like readable text
                lines = text_content.split("\n")
                readable_lines = []

                for line in lines:
                    line = line.strip()
                    if (
                        len(line) > 10
                        and len([c for c in line if c.isalpha()]) > len(line) * 0.3
                    ):
                        readable_lines.append(line)
                        if len(readable_lines) >= 10:  # Get first 10 readable lines
                            break

                if readable_lines:
                    email_data["subject"] = (
                        readable_lines[0][:100]
                        if readable_lines
                        else "MSG File Content"
                    )
                    email_data["body"] = "\n".join(readable_lines)

            return {
                "format": "msg",
                "file_path": str(file_path),
                "subject": email_data.get("subject", "MSG File"),
                "from": email_data.get("sender_email", "Unknown"),
                "sender": email_data.get("sender_email", "Unknown"),
                "to": email_data.get("display_to", ""),
                "recipient": email_data.get("display_to", ""),
                "cc": email_data.get("display_cc", ""),
                "date": email_data.get("client_submit_time", ""),
                "content": email_data.get(
                    "body", text_content[:1000]
                ),  # First 1000 chars as fallback
                "attachments": [],
                "attachment_contents": {},
                "native_parser": True,
                "parsing_method": "fallback_text_extraction",
            }

        except Exception as e:
            return {"error": f"Failed to extract MSG content: {str(e)}"}

    def _detect_attachments(self, content: bytes, email_data: Dict) -> tuple:
        """
        Attempt to detect attachments in MSG file content.
        This is a basic implementation that looks for attachment patterns.
        """
        attachments = []
        attachment_contents = {}

        try:
            # Convert content to text for pattern searching
            text_content = content.decode("utf-8", errors="ignore")
            if not text_content.strip():
                text_content = content.decode("latin-1", errors="ignore")

            # Look for common attachment patterns in the binary/text data
            # This is heuristic-based and may not catch all attachments

            # Look for filename patterns that might indicate attachments
            import re

            filename_patterns = [
                r"([a-zA-Z0-9_\-\.]+\.(pdf|txt|doc|docx|html|htm|rtf))",
                r'filename["\s]*=["\']\s*([^"\']+)',
                r'name["\s]*=["\']\s*([^"\']+)',
            ]

            potential_files = set()
            for pattern in filename_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        potential_files.add(match[0])
                    else:
                        potential_files.add(match)

            # Create basic attachment info for detected files
            for filename in potential_files:
                if "." in filename and len(filename) > 3:
                    attachment_info = {
                        "filename": filename,
                        "content_type": "application/octet-stream",
                        "size": 0,  # Unknown size in basic detection
                        "extracted_text": None,
                    }
                    attachments.append(attachment_info)

            # Try to extract any embedded text that might be attachment content
            # Look for structured content that might be from attachments
            lines = text_content.split("\n")
            current_attachment_content = []
            in_structured_content = False

            for line in lines:
                line = line.strip()

                # Heuristics for detecting structured content
                if (
                    len(line) > 20
                    and not line.startswith(("From:", "To:", "Subject:", "Date:"))
                    and len([c for c in line if c.isalpha()]) > len(line) * 0.6
                ):

                    current_attachment_content.append(line)
                    in_structured_content = True

                    # If we've collected enough structured content, it might be an attachment
                    if len(current_attachment_content) > 5:
                        content_text = "\n".join(current_attachment_content)

                        # Only include if it looks like meaningful content
                        if len(content_text) > 100:
                            # Try to associate with a detected filename
                            if attachments:
                                filename = attachments[0]["filename"]
                                attachment_contents[filename] = content_text[
                                    :1000
                                ]  # Limit size
                            else:
                                # Create a generic attachment entry
                                attachment_contents["detected_content.txt"] = (
                                    content_text[:1000]
                                )

                        current_attachment_content = []
                        in_structured_content = False

        except Exception:
            # If detection fails, return empty results
            pass

        return attachments, attachment_contents


def parse_msg_file_native(file_path: Union[str, Path]) -> Dict:
    """
    Convenience function to parse MSG file with native parser.

    Args:
        file_path: Path to the .msg file

    Returns:
        Dict containing parsed email data or error information
    """
    parser = NativeMsgParser()
    return parser.parse_msg_file(file_path)
