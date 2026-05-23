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
# 1. PAGE CONFIGURATION & UI STYLING (COLORFUL & PLAYFUL)
# =====================================================================
st.set_page_config(
    page_title="GenAI Math",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a Colorful, Primary School Student & Teacher friendly look
st.markdown("""
<style>
    /* Importing cheerful fonts (Nunito & Fredoka) from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600;700&display=swap');

    /* Applying base fonts */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    /* Styling for the Main Header (Colorful Gradient) */
    .main-header {
        font-family: 'Fredoka', sans-serif;
        font-size: 3.5rem;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4, #FFD166, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Neat and soft sub-header */
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
        text-align: center;
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 15px;
        border-left: 8px solid #4ECDC4;
        border-right: 8px solid #FFD166;
    }

    /* Badge Label (Sticker-like) */
    .badge-research {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
        color: #D81159;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 1rem;
        font-weight: 700;
        display: block;
        width: fit-content;
        margin: 0 auto 1rem auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px dashed #FFF;
    }

    /* Styling main buttons to look like plush toy buttons */
    .stButton>button {
        background-color: #FF6B6B !important;
        color: white !important;
        border-radius: 25px !important;
        border: 3px solid #FFF !important;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.6);
        background-color: #FF8787 !important;
    }

    /* Beautifying the Chat Message Box */
    .stChatMessage {
        border-radius: 20px;
        padding: 15px;
        border: 2px solid transparent;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F0F7FA;
        border-right: 3px dashed #45B7D1;
    }
    
    /* Headers inside the Sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3 {
        font-family: 'Fredoka', sans-serif;
        color: #1E3A8A;
    }
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
- Tone & Style: Friendly, educational, collaborative, enthusiastic about teaching, and highly solution-oriented. Always address the user warmly as "Wonderful Teacher".
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
2. If the user asks about topics outside of Primary School Mathematics or outside the scope of the uploaded curriculum document, decline politely by saying: "I apologize, Wonderful Teacher, but that topic is outside our current focus on developing concrete PjBL models for abstract primary school math concepts. Let us return to designing engaging primary math projects."
3. Strictly bound all mathematical explanations to the cognitive limits of primary school students (do not use advanced algebra, calculus notation, or overly complex mathematical symbols).
"""

# =====================================================================
# 3. SESSION STATE INITIALIZATION
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, Wonderful Teacher! 👋 Welcome to **GenAI Math**, your smart assistant for primary school mathematics. \n\nLet's transform difficult and abstract math materials into real and fun project adventures (PjBL) for our students! Please configure the module in the sidebar or ask for exciting ideas below!"}
    ]
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# =====================================================================
# 4. SIDEBAR CONFIGURATION (Translated & Tailored for Teachers)
# =====================================================================
with st.sidebar:
    st.title("🎒 GenAI Toolbox")
    
    api_key = st.text_input("🔑 1. Enter Gemini API Key:", type="password", help="Enter your secret key here.")
    
    st.markdown("---")
    st.subheader("🌐 Additional Learning Sources")
    
    # Toggle for Google Search Grounding
    use_web_search = st.checkbox("🔍 Enable Web Search", value=False, help="Allow the AI to search the internet for the latest materials (e.g., educational sites).")
    
    st.write("Or, upload a curriculum/textbook PDF for the AI to read.")
    
    uploaded_file = st.file_uploader("📄 Upload PDF File", type=["pdf"])
    if uploaded_file is not None and PDF_READER_AVAILABLE:
        with st.spinner("Reading textbook... 📚"):
            try:
                pdf_reader = pypdf.PdfReader(BytesIO(uploaded_file.read()))
                text = ""
                for page in range(min(len(pdf_reader.pages), 15)): # Limit to 15 pages to save context window
                    text += pdf_reader.pages[page].extract_text() + "\n"
                st.session_state.pdf_context = text
                st.success("✅ Book successfully read and memorized!")
            except Exception as e:
                st.error(f"Failed to read PDF: {e}")
    elif uploaded_file is not None and not PDF_READER_AVAILABLE:
        st.warning("Please install 'pypdf' for the document upload feature (`pip install pypdf`).")

    st.markdown("---")
    st.subheader("🏫 Project Design (PjBL)")
    phase = st.selectbox("Select Education Phase (Grade):", ["Phase A (Grades 1-2)", "Phase B (Grades 3-4)", "Phase C (Grades 5-6)"])
    concept = st.selectbox("Select Abstract Math Topic:", [
        "Fractions (Parts of a Whole)",
        "3D Geometry Nets",
        "Place Value System (Hundreds, Tens, Units)",
        "Division as Repeated Subtraction",
        "Length/Weight Measurement & Estimation",
        "Basic Data Processing & Diagrams"
    ])
    
    st.write("") # Spacer
    if st.button("✨ Create Instant PjBL Module ✨"):
        prompt = f"Please create a very fun PjBL module design for {phase} focusing on the abstract concept '{concept}'. Remember to use the 6 standard PjBL syntaxes and provide ideas for physical objects/recycled materials that students can use, and mention how AI can help the process."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# =====================================================================
# 5. MAIN CHAT INTERFACE & GEMINI API LOGIC
# =====================================================================
st.markdown('<div class="badge-research">🌟 GenAI-PjBL Learning Research 🌟</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">GenAI Math</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">🎨 Transforming abstract mathematics into concrete, meaningful, and colorful physical project-based learning experiences for primary school students. 🧩</p>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
if user_input := st.chat_input("Type here to request project ideas, class scenarios, or visual aids..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Generate AI Response
    with st.chat_message("assistant"):
        if not api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar first, Wonderful Teacher.")
        else:
            with st.spinner("Designing creative ideas for the class... 💡"):
                try:
                    # Configure API
                    genai.configure(api_key=api_key)
                    
                    # Prepare Tools (Google Search)
                    tools_config = []
                    if use_web_search:
                         # Use built-in Google Search API feature from Gemini
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
                        final_prompt = f"TEACHER REFERENCE DOCUMENT:\n{st.session_state.pdf_context}\n\nTEACHER INSTRUCTION:\n{user_input}"
                    
                    # If using web search, add a specific instruction to search for reliable educational sources
                    if use_web_search:
                        final_prompt += "\n\n(Note: The teacher allows you to search for the latest references on the internet. Please use the search feature to find ideas related to the curriculum or materials from trusted educational sites)."
                    
                    # Get Response
                    response = chat_session.send_message(final_prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"API Error Occurred: {str(e)}")

# Clear memory button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🧹 Clear the Chalkboard (Reset Chat)"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
