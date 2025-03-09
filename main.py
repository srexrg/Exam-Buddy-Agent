import streamlit as st
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools
import os


st.set_page_config(page_title="Exam Buddy", page_icon="📚", layout="wide")


os.makedirs("uploaded_docs", exist_ok=True)


knowledge_base = PDFKnowledgeBase(
    path="uploaded_docs",
    vector_db=LanceDb(
        table_name="documents",
        uri="tmp/lancedb",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    search_knowledge=True,
    show_tool_calls=True
)

youtube_summarizer_agent = Agent(
    model=Gemini(id="gemini-2.0-flash",api_key=os.getenv("GOOGLE_API_KEY")),
    tools=[YouTubeTools()],
    show_tool_calls=True,
    markdown=True,
    description="You are an AI agent that summarizes YouTube videos.",
    instructions=[
    "When given a YouTube video URL, analyze the video and provide a detailed summary.",
    "Include key points, main topics, and important timestamps in your summary.",
    "Organize the summary in a clear and concise manner.",
    "If the video contains visual elements that are crucial to understanding, mention them.",
    "For educational content, highlight main concepts and learning objectives.",
    "For reviews or comparisons, summarize pros and cons or key comparison points.",
]
)

question_generator_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    search_knowledge=True,
    add_references=True,
    show_tool_calls=True,
    markdown=True,
    description="You are an AI agent specialized in creating exam questions based on study materials in the knowledge base.",
    instructions=[
        "Create high-quality academic questions based ONLY on the content from the knowledge base.",
        "Do NOT generate questions about topics or information not explicitly found in the retrieved documents.",
        "Each question MUST be tied directly to specific content from the knowledge base.",
        "For MCQs, include 4 options with exactly one correct answer that can be verified from the source material.",
        "For long-form questions, create questions that test understanding of specific content from the source materials.",
        "Include precise citations or page references for the information used in each question.",
        "If insufficient information is available on a requested topic, state this clearly rather than fabricating content.",
        "Include the specific source document and section for each question you generate.",
        "Organize questions by topic and difficulty level when appropriate.",
        "If asked to generate questions about a topic not covered in the knowledge base, explain that you cannot generate those questions due to lack of source material."
    ]
)

def has_study_materials():
    """Check if any study materials have been uploaded"""
    return os.path.exists("uploaded_docs") and any(os.listdir("uploaded_docs"))

def summarize_youtube_video(video_url):
   
    return youtube_summarizer_agent.run(f"Summarize this YouTube video: {video_url}", stream=True)


def generate_mcq_questions(num_questions, difficulty, topics="all the topics in the knowledge base"):
    prompt = f"Generate {num_questions} multiple-choice questions at {difficulty} difficulty level"
    if topics:
        prompt += f" focusing on these topics: {topics}"
    prompt += ". Format each question with a question number, the question text, 4 options labeled A, B, C, D, and mark the correct answer. Provide an explanation for why the answer is correct."
    
    return question_generator_agent.run(prompt, stream=True)


def generate_long_questions(num_questions, marks_per_question, topics="all the topics in the knowledge base"):
    prompt = f"""Generate {num_questions} comprehensive long-form questions worth {marks_per_question} marks each.

IMPORTANT INSTRUCTIONS:
1. First, thoroughly search the knowledge base for detailed content on {topics if topics and topics.strip() else "the most important concepts in the study materials"}.
2. Generate questions ONLY about content you can find in the knowledge base. DO NOT invent or fabricate information.
3. Each question must be based on SPECIFIC sections, quotes, or passages from your knowledge base.
4. For each section of knowledge you use, include the exact document name and page/section reference.

For each question, please structure your response as follows:

### Question {marks_per_question} marks
[Clear, specific question that requires in-depth knowledge of the material]

### Source Material
[Specific document name(s) and exact page numbers/sections this question is based on]

### Key Concepts Tested
- [List 3-5 key concepts or terms from the knowledge base that this question tests]

### Model Answer
[A comprehensive model answer that would score full marks, containing ONLY information found in the knowledge base]

### Marking Scheme
- [Break down how marks would be awarded for different components of the answer]
- [Include specific terms, theories, or examples that must be mentioned]

---

If you cannot find enough relevant content in the knowledge base on the requested topics, clearly state which topics lack sufficient information rather than creating questions about them.
"""
    
    return question_generator_agent.run(prompt, stream=True)



if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"


with st.sidebar:
    st.title("📚 Exam Buddy")
    st.markdown(
        """
        Your AI study companion with:
        - 📖 **Document Search** - Query your study materials
        - 🎥 **Video Summarizer** - Get key points from lectures
        - 📝 **MCQ Generator** - Create practice questions
        - 📄 **Essay Questions** - Generate long-form questions
        """
    )
    
 
    st.header("Navigation")
    if st.button("💬 Chat Assistant", use_container_width=True):
        st.session_state.active_tab = "chat"
        st.rerun()
        
    if st.button("🎥 Video Summarizer", use_container_width=True):
        st.session_state.active_tab = "youtube"
        st.rerun()
        
    if st.button("📝 MCQ Generator", use_container_width=True):
        st.session_state.active_tab = "mcq"
        st.rerun()
        
    if st.button("📄 Long Questions", use_container_width=True):
        st.session_state.active_tab = "long"
        st.rerun()
    

    st.header("Upload Study Materials")
    uploaded_files = st.file_uploader("Upload documents", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join("uploaded_docs", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        knowledge_base.load(recreate=False)
        st.success("Documents uploaded and processed!")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


if st.session_state.active_tab == "chat":

    st.title("💬 Chat with Exam Buddy")
    

    for message in st.session_state.messages:
        with st.chat_message(
            message["role"], avatar="🧑‍💻" if message["role"] == "user" else "📚"
        ):
            st.markdown(message["content"])
    
    if not has_study_materials():
        st.warning("Please upload study materials first before chatting.")
        st.info("You can upload PDF documents using the upload section in the sidebar.")
    else:
        if prompt := st.chat_input("Ask me anything about your study materials..."):

            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
        
            
            st.session_state.messages.append({"role": "user", "content": prompt})
        
     
            with st.chat_message("assistant", avatar="📚"):
                response_container = st.empty()
                full_response = ""
                
                with st.spinner("Thinking..."):
                  
                    response_obj = agent.run(prompt, stream=True)
                    if hasattr(response_obj, 'content'):
                  
                        full_response = response_obj.content
                    else:
                  
                        for chunk in response_obj:
                            if hasattr(chunk, 'content'):
                                full_response += chunk.content
                                response_container.markdown(full_response)
                    
                  
                    response_container.markdown(full_response)
        
            
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

elif st.session_state.active_tab == "youtube":
 
    st.title("🎥 YouTube Video Summarizer")
    
    st.write("""
    ### Get quick summaries of educational videos
    Enter a YouTube URL to generate an AI summary of the video content.
    This is perfect for quickly understanding lecture content without watching the entire video.
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        video_url = st.text_input("Enter YouTube video URL")
    
    with col2:
        st.write("")
        st.write("")
        summarize_button = st.button("Summarize", use_container_width=True)
    
    if video_url and summarize_button:
        with st.spinner("Processing the video transcript..."):
            try:
            
                summary_container = st.empty()
                full_summary = ""
                
          
                streaming_response = summarize_youtube_video(video_url)
                
         
                if hasattr(streaming_response, 'content'):
                
                    full_summary = streaming_response.content
                    print(full_summary)
                    summary_container.markdown(full_summary)
                else:
                 
                    for chunk in streaming_response:
                        if hasattr(chunk, 'content'):
                            full_summary += chunk.content
                            summary_container.markdown(full_summary)
                
                
                st.success("Summary generated successfully!")
                
                
                if st.button("Add summary to chat history"):
                    st.session_state.messages.append({"role": "assistant", "content": f"**Video Summary:**\n\n{full_summary}"})
                    st.session_state.active_tab = "chat"
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error summarizing video: {e}")
                st.info("Make sure the video has captions available and the URL is correct.")

elif st.session_state.active_tab == "mcq":

    st.title("📝 Multiple Choice Question Generator")
    
    st.write("""
    ### Create practice MCQs from your study materials
    Generate custom multiple-choice questions based on your uploaded documents.
    Perfect for testing your knowledge and exam preparation.
    """)
    

    with st.form("mcq_generator_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
            topics = st.text_input("Focus topics (optional)", placeholder="Leave blank to cover all topics")
        
        with col2:
            difficulty = st.select_slider("Difficulty level", options=["Easy", "Medium", "Hard"], value="Medium")
            generate_button = st.form_submit_button("Generate MCQs", use_container_width=True)
    
 
    if generate_button:
        if has_study_materials():
            with st.spinner("Generating multiple choice questions..."):
                try:
            
                    mcq_container = st.empty()
                    full_mcqs = ""
                    
             
                    streaming_response = generate_mcq_questions(num_questions, difficulty, topics)
                    
            
                    if hasattr(streaming_response, 'content'):
         
                        full_mcqs = streaming_response.content
                        mcq_container.markdown(full_mcqs)
                    else:
             
                        for chunk in streaming_response:
                            if hasattr(chunk, 'content'):
                                full_mcqs += chunk.content
                                mcq_container.markdown(full_mcqs)
                    
           
                    if st.button("Add MCQs to chat history"):
                        st.session_state.messages.append({"role": "assistant", "content": f"**Generated MCQs:**\n\n{full_mcqs}"})
                        st.session_state.active_tab = "chat"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error generating MCQs: {e}")
        else:
            st.warning("Please upload study materials first before generating questions.")
            st.info("You can upload PDF documents using the upload section in the sidebar.")

elif st.session_state.active_tab == "long":

    st.title("📄 Long-Form Question Generator")
    
    st.write("""
    ### Create essay-style exam questions
    Generate comprehensive long-form questions with model answers based on your study materials.
    Great for deep learning and exam preparation for subjects requiring detailed responses.
    """)
    

    with st.form("long_question_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            num_questions = st.number_input("Number of questions", min_value=1, max_value=5, value=2)
            topics = st.text_input("Focus topics (optional)", placeholder="Leave blank to cover all topics")
        
        with col2:
            marks = st.select_slider("Marks per question", options=[5, 10, 15, 20], value=10)
            generate_button = st.form_submit_button("Generate Long Questions", use_container_width=True)
    

    if generate_button:
        if has_study_materials():
            with st.spinner("Generating long-form questions..."):
                try:
        
                    long_q_container = st.empty()
                    full_long_questions = ""
                    
        
                    streaming_response = generate_long_questions(num_questions, marks, topics)
                    
         
                    if hasattr(streaming_response, 'content'):
             
                        full_long_questions = streaming_response.content
                        long_q_container.markdown(full_long_questions)
                    else:
                       
                        for chunk in streaming_response:
                            if hasattr(chunk, 'content'):
                                full_long_questions += chunk.content
                                long_q_container.markdown(full_long_questions)
                    
                  
                    if st.button("Add long questions to chat history"):
                        st.session_state.messages.append({"role": "assistant", "content": f"**Generated Long-Form Questions:**\n\n{full_long_questions}"})
                        st.session_state.active_tab = "chat"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error generating long questions: {e}")
        else:
            st.warning("Please upload study materials first before generating questions.")
            st.info("You can upload PDF documents using the upload section in the sidebar.")