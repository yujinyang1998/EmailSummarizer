# PDF Email Summarizer

A simple Python web application that reads email content from a PDF file and provides AI-powered summaries.

## 🚀 Quick Start

### Automatic Setup (Recommended)

**Windows:**

```bat
setup.bat
```

**Linux/macOS:**

```bash
chmod +x setup.sh
./setup.sh
```

### Running the Application

**Windows:**

```bat
run.bat
```

**Linux/macOS:**

```bash
source venv/bin/activate
python app.py
```

Then open http://localhost:5000 in your browser.

## 📋 Manual Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment (optional):**

   ```bash
   cp .env .env.local
   # Edit .env and add your OpenAI API key for enhanced summaries
   ```

3. **Place your email PDF:**

   - Put your email PDF file in this directory
   - Name it `email.pdf`

4. **Run the application:**

   **Using run scripts (after setup):**

   ```bash
   # Windows (Double-click or run in Command Prompt)
   run.bat

   # Linux/macOS
   chmod +x run.sh && ./run.sh

   # Windows PowerShell
   .\run_app.ps1
   ```

   **Manual run:**

   ```bash
   python run.py
   ```

5. **Open browser:**
   - Go to `http://localhost:5000`
   - Click "Start Summarizing"
   - Choose summary type and generate!

## 📁 What You Need

- **Python 3.8+**
- **email.pdf** - Your email content in PDF format
- **OpenAI API key** (optional, for better summaries)

## ✨ Features

- **PDF Processing**: Automatically extracts text from PDF files
- **Email Thread Detection**: Identifies separate emails in the PDF
- **Multiple Summary Types**:
  - **Short**: 2-3 sentence overview
  - **Medium**: Comprehensive summary with key points
  - **Long**: Detailed analysis with timeline and action items
- **AI-Powered**: Uses OpenAI for intelligent summaries (optional)
- **Simple Interface**: Clean web interface for easy use
- **Copy & Share**: Easy copy-to-clipboard functionality

## 🛠 How It Works

1. **PDF Text Extraction**: Uses PyPDF2 to extract text from your email PDF
2. **Email Parsing**: Intelligently splits content into individual emails
3. **Information Extraction**: Identifies subjects, senders, dates, and content
4. **AI Summarization**: Generates summaries using OpenAI or basic text processing
5. **Web Interface**: Displays results in a user-friendly format

## 📊 Summary Types

### Short Summary

- 2-3 sentences
- Main topic and key outcomes
- Perfect for quick overviews

### Medium Summary

- Comprehensive overview
- Key participants and decisions
- Action items and outcomes
- Balanced detail level

### Long Summary

- Detailed analysis
- Complete timeline
- All participants and their roles
- Full context and background
- Comprehensive action items

## 🔧 Configuration

### Basic Setup (No API Key)

- Works with basic text summarization
- No external dependencies
- Good for simple email analysis

### Enhanced Setup (With OpenAI)

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Restart the application for enhanced AI summaries

## 📋 File Structure

```
email_summarizer/
├── app.py                     # Flask web application
├── run.py                     # Main entry point
├── email.pdf                  # Your email PDF (you provide this)
├── requirements.txt           # Python dependencies
├── .env.simple               # Environment template
├── src/
│   └── email_summarizer.py   # PDF processing and summarization
└── templates/
    ├── index.html            # Landing page
    └── summarize.html        # Main summarization interface
```

## 🔍 Troubleshooting

### "email.pdf not found"

- Make sure your PDF file is named exactly `email.pdf`
- Place it in the same directory as `run.py`

### "Could not extract text from PDF"

- Ensure your PDF contains selectable text (not just images)
- Try a different PDF viewer to verify text is extractable

### "No emails found"

- Your PDF might not have recognizable email formatting
- Try a PDF that clearly shows email headers (From:, To:, Subject:)

### Blank or poor summaries

- Add an OpenAI API key for better results
- Try different summary types
- Ensure your PDF has clear email content

## 🎯 Best Results Tips

1. **Clean PDF Format**: Use PDFs with clear email formatting
2. **Multiple Emails**: Works best with email threads or multiple emails
3. **Clear Headers**: Ensure From:, To:, Subject: fields are visible
4. **Readable Text**: Make sure text is selectable in the PDF
5. **API Key**: Add OpenAI API key for best summarization quality

## 💡 Use Cases

- **Email Archive Analysis**: Summarize old email threads
- **Meeting Follow-ups**: Extract action items from email discussions
- **Project Reviews**: Understand email-based project communications
- **Legal Discovery**: Quickly understand email content for legal matters
- **Customer Service**: Summarize customer email interactions

## 🔒 Privacy & Security

- **Local Processing**: All PDF processing happens on your machine
- **No Data Storage**: No email content is stored permanently
- **Optional Cloud**: Only uses OpenAI if you provide an API key
- **Your Control**: You control what PDFs are processed

## 📈 Future Enhancements

- Support for multiple PDF files
- Email attachment analysis
- Export summaries to different formats
- Batch processing capabilities
- Custom summary templates

## 🆘 Support

If you encounter issues:

1. Check that `email.pdf` exists and contains text
2. Verify Python dependencies are installed
3. Look at the browser console for error messages
4. Ensure the Flask server is running on port 5000

---

**Simple. Fast. Effective.**
Transform your email PDFs into actionable summaries in seconds!
