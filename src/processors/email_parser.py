"""
Email parsing module for extracting email information from text.
"""

import re
from typing import Dict, List


class EmailParser:
    """Handles parsing and structuring of email content."""

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
            line_lower = line.lower()  # Extract subject
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
