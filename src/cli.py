"""
Command Line Interface for the PDF Email Summarizer.
"""

import os
from .core.pdf_email_summarizer import PDFEmailSummarizer


def main():
    """Simple command line interface"""
    summarizer = PDFEmailSummarizer()

    print("PDF Email Summarizer")
    print("===================")
    print("Features: Parallel processing enabled for faster extraction")

    # Check if email.pdf exists
    pdf_path = "email.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found in current directory")
        print("You can also use the web interface to upload PDF files.")
        return

    print(f"Processing {pdf_path}...")

    # Ask for parallel processing configuration
    print(f"\nCurrent parallel workers: {summarizer.get_parallel_workers()}")
    workers_input = input(
        "Enter number of workers " "(or press Enter to keep current): "
    ).strip()
    if workers_input.isdigit():
        summarizer.set_parallel_workers(int(workers_input))
        print(f"Updated to {summarizer.get_parallel_workers()} workers")

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
