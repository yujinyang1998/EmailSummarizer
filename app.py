from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from src.core.pdf_email_summarizer import PDFEmailSummarizer
from src.processors.email_file_processor import EmailFileProcessor
import secrets
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(16))

# Configure upload settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "eml", "msg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize summarizer
summarizer = PDFEmailSummarizer()


def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    if not filename or "." not in filename:
        return False

    extension = "." + filename.rsplit(".", 1)[1].lower()

    # Check with EmailFileProcessor for dynamic format support
    processor = EmailFileProcessor()
    supported_formats = processor.get_supported_formats()

    return extension in supported_formats


@app.route("/")
def summarize_page():
    """Main summarization page"""
    return render_template("summarize.html")


@app.route("/api/summarize", methods=["POST"])
def summarize_emails():
    """Summarize emails from uploaded PDF, EML, MSG file or default file"""
    try:
        file_path = None

        # Check if file was uploaded
        if "email_file" in request.files:
            file = request.files["email_file"]
            if file and file.filename and allowed_file(file.filename):
                # Save uploaded file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
            elif file and file.filename:
                # Check why the file was rejected
                processor = EmailFileProcessor()

                # MSG files are now always supported with native parser
                supported_formats = ", ".join(processor.get_supported_formats())
                error_msg = (
                    f"Invalid file type. Supported formats: " f"{supported_formats}"
                )

                return jsonify({"error": error_msg}), 400

        # If no file uploaded, try default email.pdf
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), "email.pdf")
            if not os.path.exists(file_path):
                return (
                    jsonify(
                        {
                            "error": "No email file found. Please upload a "
                            "PDF, EML, or MSG file or ensure email.pdf exists "
                            "in project directory."
                        }
                    ),
                    404,
                )

        # Get summary type and API key from form data or JSON
        if request.is_json:
            data = request.get_json() or {}
            summary_type = data.get("summary_type", "medium")
            api_key = data.get("api_key")
        else:
            summary_type = request.form.get("summary_type", "medium")
            api_key = request.form.get("api_key")

        # Generate summary using the unified method
        result = summarizer.summarize_emails_from_file(file_path, summary_type, api_key)

        # Clean up uploaded file after processing
        if file_path and file_path.startswith(app.config["UPLOAD_FOLDER"]):
            try:
                os.remove(file_path)
            except OSError:
                pass  # File cleanup failed, but summary succeeded

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/formats", methods=["GET"])
def get_supported_formats():
    """Get supported file formats and dependency status"""
    try:
        processor = EmailFileProcessor()
        return jsonify(
            {
                "supported_formats": processor.get_supported_formats(),
                "dependencies": processor.check_dependencies(),
                "missing_dependencies": processor.get_missing_dependencies(),
                "success": True,
            }
        )
    except Exception as e:
        return (
            jsonify({"error": f"Failed to check formats: {str(e)}", "success": False}),
            500,
        )


if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "True").lower() == "true"
    app.run(debug=debug_mode, host="localhost", port=5000)
