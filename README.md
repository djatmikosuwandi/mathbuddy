# 📐 MathBuddy-PjBL: Generative AI-Supported PjBL Assistant

[![Live Application](https://img.shields.io/badge/Live_App-Play_Now-success?style=for-the-badge&logo=streamlit)](https://mathbuddy-pjbl.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

**MathBuddy-PjBL** is an interactive, AI-powered Teacher Assistant designed specifically for Primary School Mathematics in Indonesia. 

This application was developed to support the academic research initiative: 
> *"Implementing a Generative Artificial Intelligence–Supported Project-Based Learning Model to Improve Indonesian Primary School Students’ Understanding of Abstract Mathematics Concepts."*

🌐 **Live Demo:** [https://mathbuddy-pjbl.streamlit.app/](https://mathbuddy-pjbl.streamlit.app/)

---

## 🎯 Project Overview

Primary school students (ages 7-12) are in Piaget's **concrete-operational stage** of cognitive development, making abstract mathematical concepts (like fractions or 3D geometry nets) difficult to grasp. 

**MathBuddy-PjBL** solves this by helping teachers instantly generate **Project-Based Learning (PjBL)** modules. It acts as an expert in the Indonesian *Kurikulum Merdeka*, transforming abstract math concepts into physical, hands-on, and meaningful classroom projects using low-cost or recycled materials.

## ✨ Key Features

- **Automated PjBL Syntax Generation:** Automatically structures lesson plans into the 6 standard PjBL syntaxes used in Indonesian education (Essential Question, Project Design, Scheduling, Monitoring, Assessing, Reflection).
- **Contextual Grounding (RAG):** Teachers can upload Curriculum PDFs or Textbooks. The AI uses `pypdf` to read these documents and ground its project ideas in the provided curriculum.
- **Web Search Integration:** Built-in Google Search Tool allows the AI to fetch the latest educational references in real-time.
- **Pedagogical Guardrails:** The AI operates on a low temperature (0.3) to prevent mathematical hallucinations and is strictly constrained to primary-level cognitive capacities.
- **Secure Access (Google SSO):** Implements Google Single Sign-On (OAuth 2.0) so teachers can access the platform securely without needing to provide their own API keys. 
- **Playful UI:** A colorful, primary-school-friendly user interface built with custom CSS and Streamlit.

## 🛠️ Tech Stack

- **Frontend/UI:** [Streamlit](https://streamlit.io/)
- **LLM/AI Model:** Google Gemini 2.5 Flash (`google-generativeai`)
- **Document Processing:** `pypdf`
- **Authentication:** Google OAuth 2.0 (via Streamlit Auth packages)

## 🚀 Installation & Local Setup

To run this application locally for development, testing, or modification, follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/mathbuddy-pjbl.git](https://github.com/yourusername/mathbuddy-pjbl.git)
cd mathbuddy-pjbl
