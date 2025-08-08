from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import google.generativeai as genai

# Load environment variables
load_dotenv()

# API keys
openai_key = os.getenv("OPENAI_API_KEY")
hf_key = os.getenv("HUGGINGFACE_API_KEY")  # optional but better if you have one

if not openai_key:
    raise ValueError("OPENAI_API_KEY is missing from .env file")

# OpenAI client
client = OpenAI(api_key=openai_key)

# FastAPI app
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class Question(BaseModel):
    question: str

# # Hugging Face fallback
# def huggingface_fallback(prompt: str) -> str:
#     model_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

#     headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else {}
#     payload = {"inputs": f"Answer like you're a helpful assistant. {prompt}"}

#     try:
#         res = requests.post(model_url, headers=headers, json=payload, timeout=30)
#         if res.status_code == 200:
#             data = res.json()
#             if isinstance(data, dict) and "generated_text" in data:
#                 return data["generated_text"]
#             elif isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
#                 return data[0]["generated_text"]
#             else:
#                 return "[HF Fallback] Model returned unexpected format."
#         else:
#             return f"[HF Fallback] HTTP {res.status_code} - {res.text}"
#     except Exception as e:
#         return f"[HF Fallback] Error: {str(e)}"

def gemini_fallback(prompt: str) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return "[Gemini Fallback] No GEMINI_API_KEY in .env"

    try:
        genai.configure(api_key=gemini_key)
        # Use a current supported model
        model = genai.GenerativeModel("gemini-1.5-flash")  
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Fallback] Error: {str(e)}"
    

@app.post("/ask")
async def ask_bot(q: Question):
    prompt = f"Answer like you're a helpful assistant. {q.question}"
    try:
        # Try OpenAI first
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return {"answer": response.choices[0].message.content}

    except Exception as e:
        err_msg = str(e).lower()  # make case-insensitive

        # Trigger fallback if quota or rate limit
        if "insufficient_quota" in err_msg or "429" in err_msg:
            fallback_answer = gemini_fallback(q.question)
            return {
            "answer": fallback_answer,
            "note": "Used Gemini fallback due to OpenAI quota limit"
            }   

        else:
            return {"error": str(e)}