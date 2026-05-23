🤖 GenAI Math: Generative AI-Supported PjBL Assistant

GenAI Math is an interactive, AI-powered Teacher Assistant designed specifically for Primary School Mathematics in Indonesia.

This application was developed to support the research initiative:

"Implementing a Generative Artificial Intelligence–Supported Project-Based Learning Model to Improve Indonesian Primary School Students’ Understanding of Abstract Mathematics Concepts."

🎯 Project Overview

Primary school students (ages 7-12) are in Piaget's concrete-operational stage of cognitive development, making abstract mathematical concepts (like fractions or 3D geometry nets) difficult to grasp.

GenAI Math solves this by helping teachers instantly generate Project-Based Learning (PjBL) modules. It acts as an expert in the Indonesian Kurikulum Merdeka, transforming abstract math concepts into physical, hands-on, and meaningful classroom projects using low-cost or recycled materials.

✨ Key Features

Automated PjBL Syntax Generation: Automatically structures lesson plans into the 6 standard PjBL syntaxes used in Indonesian education (Essential Question, Project Design, Scheduling, Monitoring, Assessing, Reflection).

Contextual Grounding (RAG): Teachers can upload Curriculum PDFs or Textbooks. The AI uses pypdf to read these documents and ground its project ideas in the provided curriculum.

Web Search Integration: Built-in Google Search Tool allows the AI to fetch the latest educational references (e.g., Zenius, Kemdikbud) in real-time.

Pedagogical Guardrails: The AI operates on a low temperature (0.3) to prevent mathematical hallucinations and is strictly constrained to primary-level cognitive capacities.

Secure Access (Google SSO): Implements Google Single Sign-On (OAuth 2.0) so teachers can access the platform securely without needing to provide their own API keys. (Note: Setup requires Google Cloud Console credentials).

Playful UI: A colorful, primary-school-friendly user interface built with custom CSS and Streamlit.

🛠️ Tech Stack

Frontend/UI: Streamlit

LLM/AI Model: Google Gemini 2.5 Flash (google-generativeai)

Document Processing: pypdf

Authentication: Google OAuth 2.0 (via Streamlit Auth packages)

🚀 Installation & Local Setup

To run this application locally for development or testing, follow these steps:

1. Clone the Repository

git clone [https://github.com/yourusername/genai-math.git](https://github.com/yourusername/genai-math.git)
cd genai-math


2. Install Dependencies

Ensure you have Python 3.9+ installed. Run the following command:

pip install -r requirements.txt


(Dependencies include: streamlit, google-generativeai, pypdf)

3. Set Up Secrets (API Keys & Auth)

To keep the application secure, you must provide your Gemini API key and Google Auth credentials via Streamlit's secrets manager.

Create a folder named .streamlit in the root directory, and inside it, create a file named secrets.toml:

# .streamlit/secrets.toml

GEMINI_API_KEY = "your_google_ai_studio_api_key_here"

# If implementing Google SSO:
GOOGLE_CLIENT_ID = "your_oauth_client_id"
GOOGLE_CLIENT_SECRET = "your_oauth_client_secret"


Warning: Never commit your secrets.toml file to GitHub!

4. Run the Application

streamlit run app.py


The application will automatically open in your default web browser at http://localhost:8501.

📖 How to Use (For Teachers)

Log In: Authenticate using your Google Account.

Set Context (Optional): Upload a PDF of your current math chapter or enable "Web Search" to allow the AI to browse the internet.

Configure Project: Select the Education Phase (e.g., Phase B for Grades 3-4) and the Abstract Math Concept.

Generate: Click "Create Instant PjBL Module" to receive a comprehensive, 6-step physical project plan.

Chat: Ask follow-up questions to refine the project or generate assessment rubrics.

📄 License

This project is open-source and available under the MIT License.

Built for educational research and the advancement of primary mathematics in Indonesia.
