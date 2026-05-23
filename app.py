import streamlit as st
import google.generativeai as genai
from google.generativeai.types import Tool
import time
from io import BytesIO

# Try to import pypdf for the Contextual Grounding feature
try:
    import pypdf
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False

# =====================================================================
# 1. PAGE CONFIGURATION & UI STYLING
# =====================================================================
st.set_page_config(
    page_title="GenAI Math",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 700; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem; }
    .badge-research { background-color: #E0F2FE; color: #0369A1; padding: 0.3rem 0.8rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 1rem; }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. SYSTEM PROMPT (RESEARCH PARAMETERS)
# =====================================================================
SYSTEM_PROMPT = """
[ROLE & EXPERTISE]
You are "MathBuddy-PjBL", an artificial intelligence (AI) acting as a specialized Teacher Assistant for Primary School Mathematics in Indonesia. You are an expert in the Indonesian "Kurikulum Merdeka" (Independent Curriculum), child cognitive development psychology (specifically Piaget's concrete-operational stage for ages 7-12), and a specialist in implementing the Project-Based Learning (PjBL) model.

[CORE PURPOSE & RESEARCH GOAL]
Your primary objective is to assist teachers in constructing, designing, and implementing PjBL modules and classroom activities. The main focus of each project must center on transforming abstract mathematics concepts (such as fractions, place value, long division, and 3D geometry nets) into physical, concrete, contextual, and meaningful experiences for students, explicitly supported by Generative AI integration throughout the process.

[DOMAIN KNOWLEDGE & CONTEXT GROUNDING]
1. Scope of Material: Strictly limited to Primary School Mathematics for Phase A (Grades 1-2), Phase B (Grades 3-4), and Phase C (Grades 5-6).
2. Abstract Concepts Focus: Fractions, 3D geometry, place value systems, measurement/estimation, division as repeated subtraction, and basic data processing (charts/graphs).
3. Contextual Grounding: If the user uploads a PDF document (such as a textbook or curriculum framework) or uses the Google Search tool, you MUST prioritize the facts, chapter sequences, and core competencies within those sources as your primary reference for generating answers.

[CREATIVE CONFIGURATION & PARAMETERS]
- Tone & Style: Friendly, educational, collaborative, enthusiastic about teaching, and highly solution-oriented. Always address the user warmly as "Wonderful Teacher" or "Great Teacher".
- Temperature: Maintained at a low level (0.3) to ensure strict conceptual accuracy of mathematical formulas without hallucination, while remaining creative in designing physical, hands-on activities for students.
- Pedagogical Approach: Always recommend using low-cost, readily available, and recycled concrete objects from the child's daily environment (e.g., used cardboard, plastic straws, bottle caps, origami paper, or fruits).

[OUTPUT STRUCTURE - PJBL SYNTAX STANDARDS]
Every time a teacher asks for a project design, lesson plan template, or module solution, you MUST break it down sequentially using the 6 standard PjBL Syntaxes used in Indonesian education:
1. Step 1: Essential Question -> Craft a real-world, problem-based trigger question to stimulate critical thinking.
2. Step 2: Project Design -> Outline the rules of the project, group distributions, and the concrete physical tools/materials needed.
3. Step 3: Scheduling -> Create a realistic timeline for project completion, both inside the classroom and at home.
4. Step 4: Monitoring -> Design a teacher control sheet and specify how Generative AI can be used to provide scaffolding/guidance when students hit a roadblock.
5. Step 5: Assessing the Outcome -> Establish evaluation criteria or a rubric for the physical product made by the students, measuring their deep understanding of the math concept behind it.
6. Step 6: Reflection -> Formulate a post-project discussion guide to clear up any remaining abstract mathematical misconceptions.

[AI-SUPPORTED LEARNING INTEGRATION FEATURE]
You must provide explicit recommendations to the teacher on how to integrate Generative AI tools (e.g., guiding students to use text-to-image prompts for 3D net visualization, or asking a text-LLM for research ideas) as a tool for student groups to conduct independent research or validate their project designs during the planning and monitoring phases.

[CONSTRAINTS & GUARDRAILS]
1. NEVER provide answers consisting solely of raw numbers or theoretical formulas without explaining the accompanying physical/hands-on activity. Remember, the core of this research is overcoming abstraction.
2. If the user asks about topics outside of Primary School Mathematics or outside the scope of the uploaded curriculum document, decline politely by saying: "I apologize, Great Teacher, but that topic is outside our current focus on developing concrete PjBL models for abstract primary school math concepts. Let us return to designing engaging primary math projects."
3. Strictly bound all mathematical explanations to the cognitive limits of primary school students (do not use advanced algebra, calculus notation, or overly complex mathematical symbols).
"""

# =====================================================================
# 3. SESSION STATE INITIALIZATION
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Greetings, Wonderful Teacher! 👋 I am **GenAI Math**, your AI companion for primary school mathematics. \n\nI am ready to help you transform abstract math concepts into engaging, concrete Project-Based Learning (PjBL) modules. Please configure the parameters on the sidebar or simply ask me a question to begin!"}
    ]
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# =====================================================================
# 4. SIDEBAR CONFIGURATION
# =====================================================================
with st.sidebar:
    st.title("⚙️ GenAI-PjBL Configuration")
    
    api_key = st.text_input("1. Enter Gemini API Key:", type="password")
    
    st.markdown("---")
    st.subheader("🌐 Knowledge Sources")
    
    # Toggle for Google Search Grounding
    use_web_search = st.checkbox("Enable Google Web Search", value=False, help="Allow the AI to search the web (e.g., zenius.net) for the latest materials.")
    
    st.write("Upload a curriculum or textbook to ground the AI's knowledge.")
    
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    if uploaded_file is not None and PDF_READER_AVAILABLE:
        with st.spinner("Extracting knowledge..."):
            try:
                pdf_reader = pypdf.PdfReader(BytesIO(uploaded_file.read()))
                text = ""
                for page in range(min(len(pdf_reader.pages), 15)): # Limit to 15 pages to save context window
                    text += pdf_reader.pages[page].extract_text() + "\n"
                st.session_state.pdf_context = text
                st.success("✅ Document processed successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
    elif uploaded_file is not None and not PDF_READER_AVAILABLE:
        st.warning("Please install 'pypdf' to use the document upload feature (`pip install pypdf`).")

    st.markdown("---")
    st.subheader("🏫 PjBL Parameters")
    phase = st.selectbox("Education Phase:", ["Phase A (Grades 1-2)", "Phase B (Grades 3-4)", "Phase C (Grades 5-6)"])
    concept = st.selectbox("Abstract Concept Focus:", [
        "Fractions (Parts of a Whole)",
        "3D Geometry Nets",
        "Place Value Systems",
        "Division as Repeated Subtraction",
        "Measurement & Estimation",
        "Basic Data Processing"
    ])
    
    if st.button("Generate Instant PjBL Module"):
        prompt = f"Please create a complete PjBL module for {phase} focusing on the abstract concept of '{concept}'. Remember to follow the 6 PjBL Syntaxes and explicitly mention the integration of Generative AI."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# =====================================================================
# 5. MAIN CHAT INTERFACE & GEMINI API LOGIC
# =====================================================================
st.markdown('<div class="badge-research">🔬 RESEARCH MODEL: GenAI-Supported PjBL</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">GenAI Math</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transforming abstract mathematics into concrete, physical, and meaningful experiences for primary school students.</p>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
if user_input := st.chat_input("Ask for an engaging PjBL idea, scaffolding technique, or lesson plan..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Generate AI Response
    with st.chat_message("assistant"):
        if not api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar to activate the Assistant.")
        else:
            with st.spinner("Analyzing pedagogical frameworks... 🧠"):
                try:
                    # Configure API
                    genai.configure(api_key=api_key)
                    
                    # Persiapkan Tools (Google Search)
                    tools_config = []
                    if use_web_search:
                         # Menggunakan fitur bawaan Google Search API dari Gemini
                         tools_config.append(Tool(google_search={}))

                    # Instantiate Model with Creative Parameters and Tools
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=SYSTEM_PROMPT,
                        tools=tools_config if use_web_search else None,
                        generation_config={
                            "temperature": 0.3, # Low temperature for conceptual accuracy
                            "top_p": 0.95,
                            "top_k": 20
                        }
                    )
                    
                    # Format history for Gemini (Mapping 'assistant' to 'model')
                    gemini_history = []
                    for m in st.session_state.messages[:-1]: # Exclude the current user input
                        role = "model" if m["role"] == "assistant" else "user"
                        gemini_history.append({"role": role, "parts": [m["content"]]})
                    
                    # Start Chat Session
                    chat_session = model.start_chat(history=gemini_history)
                    
                    # Inject Contextual Grounding if PDF is uploaded
                    final_prompt = user_input
                    if st.session_state.pdf_context != "":
                        final_prompt = f"CONTEXTUAL GROUNDING DOCUMENT:\n{st.session_state.pdf_context}\n\nUSER INSTRUCTION:\n{user_input}"
                    
                    # Jika menggunakan web search, tambahkan instruksi khusus agar mencari di situs tertentu (opsional)
                    if use_web_search:
                        final_prompt += "\n\n(Instruksi Tambahan: Jika diperlukan, silakan cari informasi tambahan di internet, misalnya dari situs pendidikan seperti zenius.net atau sumber terpercaya lainnya)."
                    
                    # Get Response
                    response = chat_session.send_message(final_prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"API Error: {str(e)}")

# Clear memory button
if st.sidebar.button("🔄 Reset Conversation Memory"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
