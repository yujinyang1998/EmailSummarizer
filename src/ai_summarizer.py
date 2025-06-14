"""AI-powered summarization module using OpenAI API."""

import os
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AISummarizer:
    """Handles AI-powered summarization using OpenAI API."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    def summarize_with_openai(self, emails, summary_type="medium"):
        """Generate summary using OpenAI."""
        try:
            if not self.openai_client:
                return "OpenAI client not available"

            prompt = self._generate_prompt(emails, summary_type)

            response = self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that "
                            "summarizes email content clearly."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500 if summary_type == "short" else 1000,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            return content.strip() if content else "No summary generated"

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def _generate_prompt(self, emails, summary_type):
        """Generate prompt for AI summarization."""
        if summary_type == "short":
            base = (
                "Provide a brief 2-3 sentence summary focusing on "
                "main topic and key outcomes."
            )
        elif summary_type == "long":
            base = (
                "Provide a detailed summary including: topic, "
                "participants, key points, decisions, timeline."
            )
        else:
            base = (
                "Provide a comprehensive summary including: topic, "
                "participants, decisions, outcomes."
            )

        prompt = f"{base}\n\nEmail Thread:\n"

        for i, email in enumerate(emails):
            prompt += f"\n--- Email {i+1} ---\n"
            prompt += f"From: {email['from']}\n"
            prompt += f"To: {email['to']}\n"
            prompt += f"Subject: {email['subject']}\n"
            prompt += f"Content: {email['content'][:800]}...\n"

        return prompt
