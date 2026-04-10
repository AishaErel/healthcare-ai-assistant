import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID")

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

def clean_text(value):
    """Convert tuples/None/other types safely into clean strings."""
    if value is None:
        return ""
    if isinstance(value, tuple):
        value = value[0] if value else ""
    return str(value).strip()

def build_soap_prompt(
    raw_notes,
    patient_body_temp="",
    patient_pulse_rate="",
    patient_blood_pressure="",
    patient_history="",
    patient_context =""
):
    notes = clean_text(raw_notes)
    temp = clean_text(patient_body_temp)
    pulse = clean_text(patient_pulse_rate)
    bp = clean_text(patient_blood_pressure)
    history = clean_text(patient_history)
    context = clean_text(patient_context)

    return f"""
You are a medical documentation assistant.
Convert the following clinical information into a SOAP note.
If patient has provided history and visists, use that information to guide you as a medical record.
Do not treat past symptoms or findings as current unless mentioned in today's notes.
Prioritize today's doctor notes and structured vitals.
Use this structure exactly:

Subjective:
...

Objective:
...

Assessment:
...

Plan:
...

Rules:
- Do not invent facts.
- Use the structured vitals as the source of truth if they conflict with free-text notes.
- Do not add blood pressure, temperature, pulse, or other values unless they are provided.
- Summarize repetitive negatives instead of listing all of them.
- Ignore duplicated or nonsensical phrases.
- Expand abbreviations only when clear.
- Keep the output concise, clinical, and readable.
- If information is missing, write "Not specified".
- Return only the SOAP note and nothing else.

Patient History:
{history if history else "Not specified"}
Patient Context:
{context if context else "Not specified"}

Structured Vitals:
- Temperature: {temp if temp else "Not specified"}
- Pulse Rate: {pulse if pulse else "Not specified"}
- Blood Pressure: {bp if bp else "Not specified"}

Doctor Notes:
{notes if notes else "Not specified"}
""".strip()

def generate_soap(
    raw_notes,
    patient_body_temp="",
    patient_pulse_rate="",
    patient_blood_pressure="",
    patient_history="",
    patient_context ="",
):
    prompt = build_soap_prompt(
        raw_notes=raw_notes,
        patient_body_temp=patient_body_temp,
        patient_pulse_rate=patient_pulse_rate,
        patient_blood_pressure=patient_blood_pressure,
        patient_history=patient_history,
        patient_context =patient_context
    )

    response = model.generate_text(prompt=prompt)
    return response