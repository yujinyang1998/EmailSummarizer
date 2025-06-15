# EmailSummarizer

**AI-Powered Email Analysis Tool**

Transform your email conversations into concise, actionable summaries with advanced AI analysis.

## 🚀 Quick Start

### Option 1: Universal Launcher (Recommended)

```bash
# Works on Windows, macOS, and Linux - automatically detects platform
python launch.py
```

### Option 2: Platform-Specific Scripts

**Windows:**

```bash
# Run the setup script
scripts\setup.bat

# Start the application
scripts\run.bat
```

**macOS/Linux:**

```bash
# Make scripts executable and run
chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh && ./scripts/run.sh
```

### Option 3: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the application
python app.py
```

### Option 4: Docker

```bash
# Build and run with Docker
docker-compose -f docker/docker-compose.yml up --build
```

## 🌟 Universal Launch System

- **One Command**: `python launch.py` works on all platforms
- **Auto-Detection**: Automatically detects Windows, macOS, or Linux
- **Smart Setup**: Runs appropriate setup scripts for your platform
- **Virtual Environment**: Creates and manages virtual environment automatically
- **Dependency Installation**: Installs requirements.txt automatically
- **Browser Integration**: Opens browser automatically when ready

## 📧 Supported File Formats

- **📄 PDF**: Email conversations exported as PDF documents
- **📨 EML**: Email files from Outlook, Thunderbird, or other email clients
- **📬 MSG**: Microsoft Outlook message files (native Python support)
- **📎 Attachments**: Automatically extracts content from .txt, .html, .pdf files

## ✨ Key Features

### 🤖 AI-Powered Analysis

- **Smart Summarization**: Multiple summary types (short, detailed, bullet points)
- **Enhanced Detail Extraction**: **Automatically highlights** important information
- **Context Understanding**: Analyzes email threads and conversations
- **Attachment Processing**: Includes attachment content in analysis
- **Key Information Highlighting**: **Bold formatting** for dates, amounts, deadlines, and action items

### 📁 Universal File Support

- **No Dependencies**: MSG files work without external packages
- **Robust Parsing**: Handles various email formats and encodings
- **Error Recovery**: Graceful handling of corrupted or unusual files

### 🌐 Easy Access

- **Web Interface**: Clean, intuitive browser-based UI
- **Command Line**: CLI tool for batch processing
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🖥️ Usage

### Web Interface

1. Open browser to `http://localhost:5000`
2. Upload your email file (PDF, EML, or MSG)
3. Enter OpenAI API key (optional - for enhanced summaries)
4. Choose summary type and generate

### Command Line

```bash
# Basic CLI (processes email.pdf in current directory)
python src/cli.py

# For custom files, use the Python API or web interface
```

### Python API

```python
from src.core.pdf_email_summarizer import PDFEmailSummarizer

summarizer = PDFEmailSummarizer()
result = summarizer.summarize_emails_from_file("email.eml", "short")
print(result["summary"])
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Dependencies

All core dependencies are installed automatically:

```bash
pip install -r requirements.txt
```

**Core packages:**

- Flask (web interface)
- PyPDF2 (PDF processing)
- python-dotenv (configuration)
- OpenAI (AI summarization - optional)
- markdownify (HTML to text conversion)
- Pillow (image processing support)

**Additional packages included:**

- extract-msg (enhanced MSG file support)
- pytesseract (OCR text extraction)
- email-reply-parser (email parsing)
- pdf2image (PDF to image conversion)
- python-magic (file type detection)

**Optional enhancements:**

```bash
# For advanced HTML processing
pip install beautifulsoup4
```

## 📁 Project Structure

```
EmailSummarizer/
├── 🚀 app.py                    # Main Flask application
├── 🌟 launch.py                 # Universal cross-platform launcher
├── 📋 requirements.txt          # Python dependencies
├── 🔧 .env_example             # Environment configuration template
├── 📁 src/                     # Source code
│   ├── 🎯 core/                # Main business logic
│   ├── 🔄 processors/          # File processing engines
│   ├── 🤖 ai/                  # AI integration
│   └── 💻 cli.py               # Command line interface
├── 🎨 templates/               # Web UI templates
├── 🧪 tests/                   # Test suite
├── 🐳 docker/                  # Docker deployment
└── 📜 scripts/                 # Setup and utility scripts
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env_example`):

```bash
# OpenAI API Key (optional - for enhanced summaries)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
UPLOAD_FOLDER=uploads
```

### API Keys

- **OpenAI API**: Required for AI-powered summaries
- **Without API**: Basic summaries still work using built-in algorithms

## 🚀 Deployment

### Local Development

```bash
# Quick start with universal launcher
python launch.py

# OR direct launch
python app.py
# Access at http://localhost:5000
```

### Production with Docker

```bash
cd docker
docker-compose up -d
# Access at http://localhost:8080
```

### Cloud Deployment

The application is ready for deployment on:

- **Heroku**: Use provided Dockerfile
- **AWS**: Compatible with ECS/EC2
- **Google Cloud**: Works with Cloud Run
- **Azure**: Compatible with Container Instances

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_email_formats.py

# Test with coverage
python -m pytest --cov=src tests/
```

### Manual Testing

```bash
# Test CLI (requires email.pdf in current directory)
python src/cli.py

# Test web interface
python app.py
# Navigate to http://localhost:5000
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd EmailSummarizer

# Quick start (recommended)
python launch.py

# OR manual setup:
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Code Structure

- **`src/core/`**: Main email processing logic
- **`src/processors/`**: File format handlers (EML, MSG, PDF)
- **`src/ai/`**: AI integration and summarization
- **`templates/`**: HTML templates for web interface
- **`scripts/`**: Utility and setup scripts

## 📋 Troubleshooting

### Common Issues

**"Module not found" errors:**

```bash
pip install -r requirements.txt
```

**MSG files not processing:**

```bash
# MSG files should work natively, but for enhanced support:
pip install extract-msg
# (Note: extract-msg is already included in requirements.txt)
```

**Port already in use:**

```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Permission errors:**

```bash
# Run as administrator (Windows)
# Use sudo (Linux/Mac)
```

### Debug Mode

```bash
export FLASK_DEBUG=1
python app.py
```

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Create Pull Request

### Code Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to functions
- Include tests for new features
- Update README for user-facing changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

- **Issues**: Submit GitHub issues for bugs or feature requests
- **Documentation**: Check this README for common questions
- **Development**: Review code comments and docstrings

### Known Limitations

- **Large Files**: Performance may decrease with very large email files (>10MB)
- **Complex Formatting**: Some heavily formatted emails may lose styling
- **Attachment Types**: Only text-based attachments are processed for content

## 🎯 Roadmap

### Upcoming Features

- **Batch Processing**: Handle multiple email files at once
- **Export Options**: PDF, Word, and Excel export formats
- **Advanced Analytics**: Email sentiment analysis and threading
- **Integration APIs**: Connect with email clients and CRM systems

### Performance Improvements

- **Streaming Processing**: Handle larger files more efficiently
- **Caching**: Reduce processing time for repeated operations
- **Parallel Processing**: Multi-threaded file processing

---

**Ready to transform your email analysis workflow? Get started in minutes!** 🚀
