<!DOCTYPE html>
<html>
<head>
<title>AI Research Paper Analyzer</title>
</head>
<body>

<h1>🔬 AI Research Paper Analyzer</h1>

<h2>Overview</h2>
<p>The <strong>AI Research Paper Analyzer</strong> is a Streamlit-based web application that leverages <strong>Groq LLM</strong> and <strong>LLaMA 3</strong> models to provide intelligent and structured analysis of academic research papers. It processes PDFs through context-aware chunking, enabling scalable handling of large documents.</p>

<h2>🚀 Features</h2>

<h3>Core Functionality</h3>
<ul>
  <li>📄 <strong>PDF Upload & Extraction</strong>: Supports research paper text extraction via PyMuPDF.</li>
  <li>🔍 <strong>Smart Chunking</strong>: Efficient document handling using chunk overlap and context preservation.</li>
  <li>🧠 <strong>Multiple Analysis Modes</strong>:
    <ul>
      <li>Comprehensive Summary</li>
      <li>Critical Analysis</li>
      <li>Research Gaps Identification</li>
      <li>Future Work & Suggestions</li>
    </ul>
  </li>
</ul>

<h3>Technical Highlights</h3>
<ul>
  <li>✅ Streamlit-based UI with live progress updates</li>
  <li>⚙️ Configurable chunking and model settings</li>
  <li>🔗 Groq LLM + LLaMA 3 integration</li>
  <li>🛡️ Robust error handling and fallback logic</li>
</ul>

<h2>🛠️ Installation</h2>

<h3>Prerequisites</h3>
<ul>
  <li>Python &gt;= 3.8</li>
  <li>pip</li>
</ul>

<h3>Setup Instructions</h3>
<ol>
  <li>
    <strong>Clone the repository:</strong>
    <pre><code class="language-bash">
git clone https://github.com/yourusername/ai-research-analyzer.git
cd ai-research-analyzer
    </code></pre>
  </li>
  <li>
    <strong>Install dependencies:</strong>
    <pre><code class="language-bash">
pip install -r requirements.txt
    </code></pre>
  </li>
  <li>
    <strong>Create environment configuration:</strong>
    <p>Create a <code>.env</code> file in the root directory and add:</p>
    <pre><code class="language-env">
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-70b-8192
    </code></pre>
  </li>
</ol>

<h2>🗂️ Project Structure</h2>
<pre><code class="language-text">
ai-research-analyzer/
├── app.py                # Main Streamlit app
├── config.py             # Config settings for model and chunk size
├── llm_utils.py          # Handles LLM interaction
├── pdf_utils.py          # PDF text extraction and preprocessing
├── requirements.txt      # Dependency list
└── temp_uploaded_pdfs/   # Temporary storage for uploaded PDFs
</code></pre>

<h2>🧪 Usage Guide</h2>

<h3>Start the Application</h3>
<pre><code class="language-bash">
streamlit run app.py
</code></pre>

<h3>Step-by-Step Usage</h3>
<ol>
  <li><strong>Upload PDF</strong>: Drag-and-drop or browse to upload your paper (PDF format).</li>
  <li><strong>Select Analysis Options</strong>: Choose from Summary, Critical Review, Research Gaps, and Future Work.</li>
  <li><strong>Click "🚀 Analyze Paper"</strong>: View results in expandable sections with progress indicators.</li>
</ol>

<h2>⚙️ Configuration Options</h2>
<p>Located in <code>config.py</code>:</p>
<pre><code class="language-python">
PROJECT_NAME: str = "AI Research Paper Analyzer (Streamlit)"
LLM_MODEL: str = "llama3-70b-8192"
CHUNK_TARGET_CHAR_COUNT: int = 12000
CHUNK_OVERLAP_CHAR_COUNT: int = 500
</code></pre>

<h2>📌 Technical Details</h2>

<h3>PDF Handling</h3>
<ul>
  <li>Powered by PyMuPDF</li>
  <li>Supports multi-page academic PDFs</li>
  <li>Detects and skips corrupt or empty files</li>
</ul>

<h3>LLM Integration</h3>
<ul>
  <li>Uses Groq API with LLaMA 3</li>
  <li>Processes large documents using context-aware chunking</li>
  <li>Retry logic implemented for failed or timed-out requests</li>
</ul>

<h3>UI Components</h3>
<ul>
  <li>Built with Streamlit</li>
  <li>Sidebar for input controls and model override</li>
  <li>Real-time progress tracking and expandable result sections</li>
</ul>

<h2>❗ Error Handling</h2>

<h3>PDF Issues</h3>
<ul>
  <li>Unsupported file format</li>
  <li>Corrupt or empty documents</li>
</ul>

<h3>LLM Issues</h3>
<ul>
  <li>API rate limits or connectivity issues</li>
  <li>Retry mechanism for transient errors</li>
</ul>

<h2>📦 Development</h2>

<h3>Adding New Features</h3>
<ol>
  <li>Fork this repository.</li>
  <li>
    Create a new branch:
    <pre><code class="language-bash">
git checkout -b feature/your-feature-name
    </code></pre>
  </li>
  <li>
    Make your changes and commit:
    <pre><code class="language-bash">
git commit -m "Add new feature"
    </code></pre>
  </li>
  <li>
    Push to your fork:
    <pre><code class="language-bash">
git push origin feature/your-feature-name
    </code></pre>
  </li>
  <li>Submit a pull request.</li>
</ol>

<h3>Run Tests</h3>
<pre><code class="language-bash">
python -m pytest tests/
</code></pre>

<h2>🤝 Contributing</h2>
<p>We welcome contributions! Please review the contributing guidelines and code of conduct before submitting a pull request.</p>

<h2>📜 License</h2>
<p>This project is licensed under the MIT License – see the <code>LICENSE</code> file for full details.</p>

<h2>🧑‍💻 Support</h2>
<ul>
  <li>For bugs or issues, please open a GitHub Issue.</li>
  <li>For feature requests or inquiries, email: <code>[your-email@example.com]</code></li>
</ul>

<h2>🙏 Acknowledgments</h2>
<ul>
  <li>Groq LLM API</li>
  <li>Meta's LLaMA 3</li>
  <li>Streamlit Framework</li>
  <li>PyMuPDF Library</li>
</ul>

</body>
</html>
