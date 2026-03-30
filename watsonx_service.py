import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)

model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 300,
        "temperature": 0.2
    }
)

def build_soap_prompt(raw_notes, patient_context=""):
    return f"""
You are a 24/7 available, intelligent, educated AI healthcare documentation assistant. Doctor may ask you about healthcare related questions
or may ask your opinion on specific drug or illness, make educated guesses based on your knwoledge and if you are not sure about it state that you are not sure

When doctor asks, convert the doctor's shorthand notes into a SOAP medical record.

Rules:
- Do not invent facts
- Do not add new information such as blood pressure, temperature (if those are not provided leave as blank)
- Expand abbreviations only when clear
- Keep the output concise and clinical
- If information is missing, (including blood pressure, temparture, etc) values write "Not specified"

Return only in this format:

Subjective:
...

Objective:
...

Assessment:
...

Plan:
...

Patient context:
{patient_context}

Doctor notes:
{raw_notes}
""".strip()

def generate_soap(raw_notes, patient_context=""):
    prompt = build_soap_prompt(raw_notes, patient_context)
    response = model.generate_text(prompt=prompt)
    return response