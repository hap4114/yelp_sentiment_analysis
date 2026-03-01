# 🧠 LLM-Based Yelp Review Rating & AI Feedback System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LLM](https://img.shields.io/badge/LLM-API-green)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)

A production-style AI web application that uses Large Language Models (LLMs) to classify Yelp reviews into star ratings and power a dual-dashboard intelligent feedback system.

The project explores prompt engineering strategies, structured JSON enforcement, evaluation techniques, and full-stack AI integration.


## 📌 Features

- ⭐ 1–5 Star Rating Prediction via LLM  
- 🧠 Multiple Prompt Engineering Techniques  
- 📦 Structured JSON Output Enforcement  
- 👤 Public User Feedback Dashboard  
- 🔐 Admin Dashboard with Authentication  
- 📊 AI-Generated Summaries & Recommended Actions  
- 🗄 Shared Supabase Database  
- 🌐 Fully Deployable Architecture  

---

## 🏗 Tech Stack

### 🧠 AI Layer
- LLM API (Gemini / OpenRouter / OpenAI configurable)
- Prompt Engineering
- Structured Output Validation

### 🖥 Backend
- Python
- REST-style LLM client abstraction
- Supabase SDK

### 🎨 Frontend
- Streamlit Web Application
- Admin Authentication Logic

### 🗄 Database
- Supabase (PostgreSQL backend)

### 🚀 Deployment
- Railway / Render / Cloud Platform
- Environment-based configuration

---

## 📂 Project Structure

dataset/ # Yelp dataset samples

documents/ # Reports & documentation

llm_client.py # LLM API integration

prompts.py # Prompt templates & versions

supabase_client.py # Database interaction

utils.py # Helper functions

user_dashboard_app.py # Public dashboard

updated_user_dashboard.py # Enhanced user dashboard

admin_dashboard_with_auth.py # Admin dashboard with auth

feedback_data.csv # Sample stored feedback

requirements.txt # Dependencies

env_example.sh # Environment variables template


---

## ⚡ Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/hap4114/yelp_sentiment_analysis.git
cd yelp_sentiment_analysis
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure Environment Variables

Create a .env file and add:

LLM_API_KEY=your_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
4️⃣ Run User Dashboard
python user_dashboard_app.py
5️⃣ Run Admin Dashboard
python admin_dashboard_with_auth.py
