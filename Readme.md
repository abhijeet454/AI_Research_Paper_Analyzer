```markdown
# 🔬 AI Research Paper Analyzer

## Overview
The **AI Research Paper Analyzer** is a Streamlit-based web application that leverages **Groq LLM** and **LLaMA 3** models to provide intelligent and structured analysis of academic research papers. It processes PDFs through context-aware chunking, enabling scalable handling of large documents.

## 🚀 Features

### Core Functionality
- 📄 **PDF Upload & Extraction**: Supports research paper text extraction via PyMuPDF.
- 🔍 **Smart Chunking**: Efficient document handling using chunk overlap and context preservation.
- 🧠 **Multiple Analysis Modes**:
  - Comprehensive Summary
  - Critical Analysis
  - Research Gaps Identification
  - Future Work & Suggestions

### Technical Highlights
- ✅ Streamlit-based UI with live progress updates
- ⚙️ Configurable chunking and model settings
- 🔗 Groq LLM + LLaMA 3 integration
- 🛡️ Robust error handling and fallback logic

## 🛠️ Installation

### Prerequisites
- Python >= 3.8
- pip

### Setup Instructions
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/ai-research-analyzer.git](https://github.com/yourusername/ai-research-analyzer.git)
    cd ai-research-analyzer
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create environment configuration:**
    Create a `.env` file in the root directory and add:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    LLM_MODEL=llama3-70b-8192
    ```

## 🗂️ Project Structure
```text
ai-research-analyzer/
├── app.py                # Main Streamlit app
├── config.py             # Config settings for model and chunk size
├── llm_utils.py          # Handles LLM interaction
├── pdf_utils.py          # PDF text extraction and preprocessing
├── requirements.txt      # Dependency list
└── temp_uploaded_pdfs/   # Temporary storage for uploaded PDFs
```

## 🧪 Usage Guide

### Start the Application
```bash
streamlit run app.py
```

### Step-by-Step Usage
1.  **Upload PDF**: Drag-and-drop or browse to upload your paper (PDF format).
2.  **Select Analysis Options**: Choose from Summary, Critical Review, Research Gaps, and Future Work.
3.  **Click "🚀 Analyze Paper"**: View results in expandable sections with progress indicators.

## ⚙️ Configuration Options
Located in `config.py`:
```python
PROJECT_NAME: str = "AI Research Paper Analyzer (Streamlit)"
LLM_MODEL: str = "llama3-70b-8192"
CHUNK_TARGET_CHAR_COUNT: int = 12000
CHUNK_OVERLAP_CHAR_COUNT: int = 500
```

## 📌 Technical Details

### PDF Handling
- Powered by PyMuPDF
- Supports multi-page academic PDFs
- Detects and skips corrupt or empty files

### LLM Integration
- Uses Groq API with LLaMA 3
- Processes large documents using context-aware chunking
- Retry logic implemented for failed or timed-out requests

### UI Components
- Built with Streamlit
- Sidebar for input controls and model override
- Real-time progress tracking and expandable result sections

## ❗ Error Handling

### PDF Issues
- Unsupported file format
- Corrupt or empty documents

### LLM Issues
- API rate limits or connectivity issues
- Retry mechanism for transient errors

## 📦 Development

### Adding New Features
1.  Fork this repository.
2.  Create a new branch:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3.  Make your changes and commit:
    ```bash
    git commit -m "Add new feature"
    ```
4.  Push to your fork:
    ```bash
    git push origin feature/your-feature-name
    ```
5.  Submit a pull request.

### Run Tests
```bash
python -m pytest tests/
```

## 🤝 Contributing
We welcome contributions! Please review the contributing guidelines and code of conduct before submitting a pull request.

## 📜 License
This project is licensed under the MIT License – see the `LICENSE` file for full details.

## 🧑‍💻 Support
- For bugs or issues, please open a GitHub Issue.
- For feature requests or inquiries, email: `[your-email@example.com]`

## 🙏 Acknowledgments
- Groq LLM API
- Meta's LLaMA 3
- Streamlit Framework
- PyMuPDF Library
```