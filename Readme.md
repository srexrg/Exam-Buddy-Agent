# Exam Buddy 📚

An AI-powered study companion that helps students prepare for exams through intelligent document search, video summarization, and automated question generation.




https://github.com/user-attachments/assets/44714450-b60c-4a07-8083-54baa257318f



## 🌟 Features

- **📖 Document Search**: Upload and query your study materials (PDFs) using natural language
- **🎥 Video Summarizer**: Get concise summaries of educational YouTube videos
- **📝 MCQ Generator**: Create custom multiple-choice questions from your study materials
- **📄 Essay Questions**: Generate long-form questions with model answers for practice

## 🛠️ Tech Stack

- **Agentic Framework**: [Agno](https://www.agno.com/)
- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **AI Models**:
  - [OpenAI GPT-4o](https://openai.com) for chat functionality and question generation
  - [Google Gemini](https://ai.google.dev/) for YouTube video summarization
- **Vector Database**: [LanceDB](https://lancedb.com/) for efficient document retrieval
- **Document Processing**: PDF extraction and vectorization

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key (for GPT-4o and embeddings)
- Google API key (for Gemini model)

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/srexrg/exam-buddy-agent.git
   cd exam-buddy-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## 🚀 Usage

1. Start the application:
   ```bash
   streamlit run main.py
   ```

2. Access the application in your browser at `http://localhost:8501`

3. Navigate through the tabs to use different features:
   - **Chat Assistant**: Ask questions about your uploaded documents
   - **Video Summarizer**: Get summaries of YouTube lectures
   - **MCQ Generator**: Create practice multiple-choice questions
   - **Long Questions**: Generate essay-style questions

## 🗂️ Project Structure

```
exam-buddy/
├── .env                  # Environment variables and API keys
├── .gitignore            # Git ignore file
├── main.py               # Main application file
├── tmp/                  # Temporary storage directory
│   └── lancedb/          # LanceDB database files
└── uploaded_docs/        # Directory for storing uploaded PDFs
```

## 📝 How It Works

1. **Document Processing**:
   - Upload PDF documents through the sidebar
   - Documents are vectorized and stored in LanceDB
   - Knowledge base provides semantic search capabilities

2. **Chat Interface**:
   - Ask questions about your study materials
   - AI agent searches the knowledge base for relevant information
   - Get contextual answers based on your documents

3. **YouTube Summarization**:
   - Enter a YouTube URL to process the video
   - Gemini AI analyzes the video content
   - Receive a structured summary with key points

4. **Question Generation**:
   - Generate MCQs with adjustable difficulty
   - Create long-form questions with model answers
   - Questions are based on your uploaded study materials

## 🔒 API Key Security

Note: This application requires API keys for OpenAI and Google. Make sure to:
- Keep your API keys secure
- Never expose your `.env` file
- Be aware of API usage costs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
