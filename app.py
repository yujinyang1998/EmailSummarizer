from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from src.email_summarizer import PDFEmailSummarizer
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(16))

# Initialize summarizer
summarizer = PDFEmailSummarizer()


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/summarize")
def summarize_page():
    """Summarization page"""
    return render_template("summarize.html")


@app.route("/api/summarize", methods=["POST"])
def summarize_emails():
    """Summarize emails from PDF"""
    try:
        data = request.get_json() or {}
        summary_type = data.get("summary_type", "medium")

        # Check if PDF exists
        pdf_path = os.path.join(os.path.dirname(__file__), "email.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": "email.pdf not found"}), 404

        # Generate summary
        result = summarizer.summarize_pdf_emails(pdf_path, summary_type)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(
        debug=os.getenv("DEBUG", "True").lower() == "true", host="localhost", port=5000
    )
