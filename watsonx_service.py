import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID")

if not API_KEY:
    raise ValueError("Missing WATSONX_APIKEY")
if not URL:
    raise ValueError("Missing WATSONX_URL")
if not PROJECT_ID:
    raise ValueError("Missing WATSONX_PROJECT_ID")
if not MODEL_ID:
    raise ValueError("Missing WATSONX_MODEL_ID")

credentials = Credentials(
    url=URL,
    api_key=API_KEY,
)

model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 260,
        "temperature": 0.1,
        "repetition_penalty": 1.05,
    },
)


def clean_text(value) -> str:
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
    patient_context="",
) -> str:
    notes = clean_text(raw_notes)
    temp = clean_text(patient_body_temp)
    pulse = clean_text(patient_pulse_rate)
    bp = clean_text(patient_blood_pressure)
    history = clean_text(patient_history)
    context = clean_text(patient_context)

    return f"""
You are a medical documentation assistant.
Convert the clinical information below into a SOAP note.

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
- Use only information explicitly provided in today's doctor notes, structured vitals, patient history, and patient context.
- Do not invent facts.
- Do not repeat these instructions.
- Do not include any text before "Subjective:" or after the Plan section.
- Do not treat past symptoms or past findings as current unless mentioned in today's doctor notes.
- Use structured vitals as the source of truth if they conflict with free-text notes.
- Do not add blood pressure, temperature, pulse, medications, diagnoses, tests, follow-up, or treatments unless they are explicitly provided.
- Patient history and patient context may be used only as background context. Do not convert old history into today's symptoms or today's plan unless explicitly stated.
- Keep the output concise, clinical, and readable.
- If information is missing in a section, write "Not specified".

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

Return only the SOAP note.
""".strip()


def build_retry_prompt(
    existing_soap,
    retry_feedback,
    raw_notes,
    patient_body_temp="",
    patient_pulse_rate="",
    patient_blood_pressure="",
    patient_history="",
    patient_context="",
) -> str:
    soap = clean_text(existing_soap)
    feedback = clean_text(retry_feedback)
    notes = clean_text(raw_notes)
    temp = clean_text(patient_body_temp)
    pulse = clean_text(patient_pulse_rate)
    bp = clean_text(patient_blood_pressure)
    history = clean_text(patient_history)
    context = clean_text(patient_context)

    return f"""
You are a medical documentation assistant.
Revise the existing SOAP note using the user's feedback.

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
- Revise the existing SOAP note based on the user's feedback.
- Keep correct content from the existing SOAP note unless the feedback requires changing it.
- Use only information explicitly provided in today's doctor notes, structured vitals, patient history, patient context, and the user's feedback.
- Do not invent facts.
- Do not include any text before "Subjective:" or after the Plan section.
- Do not treat past symptoms or past findings as current unless mentioned in today's doctor notes.
- Use structured vitals as the source of truth if they conflict with free-text notes.
- Do not add blood pressure, temperature, pulse, medications, diagnoses, tests, follow-up, or treatments unless they are explicitly provided.
- If information is missing in a section, write "Not specified".

User Feedback:
{feedback if feedback else "Not specified"}

Existing SOAP Note:
{soap if soap else "Not specified"}

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

Return only the revised SOAP note.
""".strip()


def sanitize_soap_output(text: str) -> str:
    if not text:
        return ""

    lines = [line.rstrip() for line in text.splitlines()]

    start_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Subjective:"):
            start_index = i
            break

    if start_index is None:
        return text.strip()

    kept = []
    for line in lines[start_index:]:
        stripped = line.strip().lower()

        if stripped.startswith("do not hallucinate"):
            continue
        if stripped.startswith("rules:"):
            continue
        if stripped.startswith("return only"):
            continue

        kept.append(line)

    return "\n".join(kept).strip()


def validate_soap_output(text: str) -> str:
    required_headers = ["Subjective:", "Objective:", "Assessment:", "Plan:"]
    missing = [header for header in required_headers if header not in text]
    if missing:
        raise ValueError(f"SOAP output missing sections: {', '.join(missing)}")
    return text


def _finalize_response(response) -> str:
    if response is None:
        raise ValueError("Watsonx returned None")

    if not isinstance(response, str):
        response = str(response)

    cleaned = sanitize_soap_output(response.strip())
    validated = validate_soap_output(cleaned)

    if not validated:
        raise ValueError("Watsonx returned blank SOAP output")

    return validated


def generate_soap(
    raw_notes,
    patient_body_temp="",
    patient_pulse_rate="",
    patient_blood_pressure="",
    patient_history="",
    patient_context="",
) -> str:
    prompt = build_soap_prompt(
        raw_notes=raw_notes,
        patient_body_temp=patient_body_temp,
        patient_pulse_rate=patient_pulse_rate,
        patient_blood_pressure=patient_blood_pressure,
        patient_history=patient_history,
        patient_context=patient_context,
    )

    response = model.generate_text(prompt=prompt)
    return _finalize_response(response)


def retry_soap(
    existing_soap,
    retry_feedback,
    raw_notes,
    patient_body_temp="",
    patient_pulse_rate="",
    patient_blood_pressure="",
    patient_history="",
    patient_context="",
) -> str:
    prompt = build_retry_prompt(
        existing_soap=existing_soap,
        retry_feedback=retry_feedback,
        raw_notes=raw_notes,
        patient_body_temp=patient_body_temp,
        patient_pulse_rate=patient_pulse_rate,
        patient_blood_pressure=patient_blood_pressure,
        patient_history=patient_history,
        patient_context=patient_context,
    )

    response = model.generate_text(prompt=prompt)
    return _finalize_response(response)