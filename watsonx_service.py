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
    "max_new_tokens": 220,
    "temperature": 0.1,
    "repetition_penalty": 1.05
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
SYSTEM ROLE:
You are a clinical medical documentation assistant designed to generate accurate, structured SOAP notes from physician inputs.

You operate in a HIGH-RISK medical environment. Accuracy, consistency, and non-fabrication are critical.

--------------------------------------------------
INSTRUCTION PRIORITY (FOLLOW STRICTLY IN ORDER):
1. DO NOT hallucinate or invent any information.
2. PRIORITIZE today's doctor notes over all other inputs.
3. USE structured vitals as the source of truth if conflicts occur.
4. USE patient history ONLY as supporting context (NOT current condition unless explicitly stated).
5. IF data is missing -> explicitly write "Not specified".
6. OUTPUT must strictly follow the SOAP format (no deviations).

--------------------------------------------------
TASK:
Convert the provided clinical input into a SOAP note.

--------------------------------------------------
OUTPUT FORMAT (STRICT — DO NOT MODIFY):

Subjective:
<Patient-reported symptoms, complaints, and relevant history>

Objective:
<Observed findings, vitals, measurable data>

Assessment:
<Clinical interpretation, possible diagnoses, reasoning>

Plan:
<Treatment plan, medications, next steps>

--------------------------------------------------
RULES & GUARDRAILS:

DO:
- Keep language clinical, concise, and professional
- Resolve contradictions using instruction priority
- Normalize messy or duplicated notes
- Expand abbreviations ONLY when medically certain
- Summarize repetitive negatives (e.g., "denies fever, chills, nausea")

DO NOT:
- Do NOT add new symptoms, vitals, or diagnoses
- Do NOT assume missing values
- Do NOT infer beyond provided data
- Do NOT mix past history with current symptoms
- Do NOT output anything outside SOAP sections

--------------------------------------------------
EDGE CASE HANDLING:

- If notes are incomplete -> fill sections with "Not specified"
- If vitals are missing -> do NOT generate them
- If notes are noisy -> clean and extract only medically relevant info
- If conflicting data exists:
  -> Structured vitals > Doctor notes > Patient history

--------------------------------------------------
FEW-SHOT EXAMPLE:

INPUT:
Doctor Notes:
"Patient complains of headache for 2 days, denies fever. BP slightly elevated."

Vitals:
BP: 140/90
Temp: Not specified
Pulse: 72

History:
Hypertension

OUTPUT:
Subjective:
Patient reports headache for 2 days. Denies fever.

Objective:
Blood pressure: 140/90. Pulse: 72. Temperature: Not specified.

Assessment:
Headache. History of hypertension noted.

Plan:
Monitor blood pressure. Follow-up if symptoms persist.

--------------------------------------------------
INPUT DATA:

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

Return only the completed SOAP note.

Use exactly these section headers and include all four sections even if some content is "Not specified":

Subjective:
Objective:
Assessment:
Plan:

Do not return a sentence fragment.
Do not return an explanation.
Do not return any text before or after the SOAP note.

Begin now.
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
        patient_context=patient_context
    )

    response = model.generate_text(prompt=prompt)
    return response