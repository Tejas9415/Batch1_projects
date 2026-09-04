import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not GROQ_API_KEY :
    raise EnvironmentError(
        "Didn't get any GROQ API KEY from the environment, paste your GROQ API KEY in .env file"
    )
def get_llm(temperature: float= 0.2):
    return ChatGroq(model= GROQ_MODEL, api_key= GROQ_API_KEY, temperature= temperature)