"""AI-powered summarization module using OpenAI API."""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AISummarizer:
    """Handles AI-powered summarization using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    def set_api_key(self, api_key: str):
        """Set or update the OpenAI API key."""
        self.openai_api_key = api_key
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None

    def summarize_with_openai(self, emails, summary_type="medium"):
        """Generate summary using OpenAI."""
        try:
            if not self.openai_client:
                return "OpenAI client not available"

            prompt = self._generate_prompt(emails, summary_type)

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a highly skilled email analysis assistant. "
                            "Analyze email content thoroughly and provide structured summaries "
                            "with clear highlighting of important details."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800 if summary_type == "short" else 1500,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            return content.strip() if content else "No summary generated"

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def _generate_prompt(self, emails, summary_type):
        """Generate enhanced prompt for AI summarization with detailed analysis."""

        # Enhanced base prompts with specific instructions for detail and highlighting
        if summary_type == "short":
            base = (
                "Provide a concise 3-4 sentence summary with the following structure:\n"
                "1. **Main Topic**: What is the primary subject matter?\n"
                "2. **Key Participants**: Who are the main people involved?\n"
                "3. **Critical Outcomes**: What important decisions, actions, or deadlines were established?\n"
                "4. **Next Steps**: What follow-up actions are required?\n\n"
                "Use **bold text** to highlight the most important information such as deadlines, "
                "dollar amounts, names, decisions, and action items."
            )
        elif summary_type == "long":
            base = (
                "Provide a comprehensive detailed summary with the following structure:\n"
                "## Executive Summary\n"
                "Brief overview of the main topic and outcomes.\n\n"
                "## Key Participants\n"
                "List all important people and their roles.\n\n"
                "## Important Details\n"
                "- **Deadlines**: All dates and timeline information\n"
                "- **Financial Information**: Any monetary amounts, budgets, costs\n"
                "- **Decisions Made**: Key choices and determinations\n"
                "- **Action Items**: Specific tasks and responsibilities assigned\n"
                "- **Issues/Concerns**: Problems raised and their status\n\n"
                "## Next Steps & Follow-up\n"
                "What needs to happen next and who is responsible.\n\n"
                "Use **bold text** for all critical information including names, dates, amounts, "
                "and action items. Use bullet points for clarity."
            )
        else:  # medium
            base = (
                "Provide a well-structured summary with the following format:\n"
                "**Topic**: Main subject and context\n"
                "**Participants**: Key people involved (highlight names in **bold**)\n"
                "**Important Details**:\n"
                "- **Deadlines/Dates**: Any time-sensitive information\n"
                "- **Key Decisions**: Important choices made\n"
                "- **Action Items**: Tasks assigned with responsible parties\n"
                "- **Financial/Numerical Data**: Dollar amounts, quantities, etc.\n"
                "**Outcomes**: Results achieved or expected\n"
                "**Next Steps**: Required follow-up actions\n\n"
                "Emphasize critical information with **bold formatting** including all names, "
                "dates, amounts, deadlines, and action items."
            )

        prompt = f"{base}\n\n=== EMAIL THREAD ANALYSIS ===\n"

        for i, email in enumerate(emails):
            prompt += f"\n--- Email {i+1} ---\n"
            prompt += f"From: {email['from']}\n"
            prompt += f"To: {email['to']}\n"
            prompt += f"Subject: {email['subject']}\n"
            prompt += f"Date: {email.get('date', 'Not specified')}\n"

            # Include more content for better analysis
            content_limit = 1200 if summary_type == "long" else 1000
            content = email["content"][:content_limit]
            if len(email["content"]) > content_limit:
                content += "...[content truncated]"
            prompt += f"Content: {content}\n"

        # Add specific instructions for highlighting
        prompt += (
            "\n=== ANALYSIS INSTRUCTIONS ===\n"
            "Please analyze the entire email thread and provide a summary that:\n"
            "1. Identifies ALL important details (dates, names, amounts, deadlines)\n"
            "2. Highlights critical information using **bold text**\n"
            "3. Organizes information logically and clearly\n"
            "4. Includes specific action items and who is responsible\n"
            "5. Notes any unresolved issues or pending decisions\n"
            "6. Provides clear next steps and timelines\n\n"
            "Remember: Use **bold text** for all names, dates, dollar amounts, "
            "deadlines, and action items to make them easily scannable."
        )

        return prompt
