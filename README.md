# AskMe Bot

A minimal AI-powered chatbot using React + FastAPI + OpenAI GPT API.

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
