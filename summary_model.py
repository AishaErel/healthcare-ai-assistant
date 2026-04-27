import os
from dotenv import load_dotenv
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from cloudant_service import search_patient
from patient_context_for_model import build_patient_context_text
import streamlit as st

load_dotenv()

API_KEY = st.secrets["WATSONX_APIKEY"] or os.getenv["WATSONX_APIKEY"]
URL = st.secrets["WATSONX_URL"] or os.getenv["WATSONX_URL"]
PROJECT_ID = st.secrets["WATSONX_PROJECT_ID"] or os.getenv["WATSONX_PROJECT_ID"]
MODEL_ID = st.secrets["WATSONX_MODEL_ID"] or os.getenv["WATSONX_MODEL_ID"]

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)
nlp_model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "temperature": 0.2,
        "max_tokens": 200
    }
)

summary_model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 500,
        "temperature": 0,
        "repetition_penalty": 1.05,
        "stop_sequences": ["<|eom_id|>"]
    }
)

def summarization_prompt_contextless(patient_context):
    return f"""You are a healthcare assistant. Your role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's basic medical history and past visit records, focusing on most relevant history that would be useful to an upcoming visit. Not all records provided may be relevant.
Only refer to the information obtained from the retrieved records.
If there is no past visit history, report that there is no past history.
If there is not sufficient past data to provide a detailed summary, summarize what information was available and note that there was not much information.
If including medications, include dates prescribed and the duration.
Include dates for context when summarizing past visits.

Here is the information you need to summarize:
{patient_context}

    """.strip()
    
def summarization_prompt_context(basic_history, past_records, rfv=None):
    return f"""SYSTEM ROLE:
You are a healthcare summarization assistant helping medical professionals quickly understand a patient’s history before a visit.

Your output must be structured, concise, and clinically relevant.

--------------------------------------------------
INSTRUCTION PRIORITY:

1. ONLY use provided data (NO hallucination)
2. PRIORITIZE relevance to upcoming visit (Reason for Visit if provided)
3. SUMMARIZE — do NOT rewrite everything
4. INCLUDE dates whenever available
5. If data is insufficient → explicitly state it

--------------------------------------------------
TASK:
Generate a structured summary of the patient’s medical history and past visits.

--------------------------------------------------
OUTPUT FORMAT (STRICT):

Patient Summary:

1. Key Medical History:
- ...

2. Relevant Past Visits:
- [Date]&#58; <summary>
- [Date]&#58; <summary>

3. Medications (if available):
- Medication (Date prescribed, duration)

4. Key Observations:
- Patterns, recurring issues, risks

5. Data Gaps:
- Missing or insufficient information

--------------------------------------------------
RULES & GUARDRAILS:

DO:
- Focus on clinically relevant information
- Prioritize conditions related to: {rfv if rfv else "general health"}
- Use bullet points for clarity
- Keep it concise but informative
- Highlight trends (chronic illness, repeat visits)

DO NOT:
- Do NOT make it a email or provide a email signature
- Do NOT include irrelevant details
- Do NOT invent missing history
- Do NOT assume diagnoses
- Do NOT repeat raw data verbatim

--------------------------------------------------
EDGE CASE HANDLING:

- No past records → "No past visit history available"
- Sparse data → summarize and note limitation
- Conflicting data → present neutrally without resolving

--------------------------------------------------
FEW-SHOT EXAMPLE:

INPUT:
History: Hypertension, Diabetes
Records:
- Jan 2024: Routine checkup, BP high
- Mar 2024: Complained of fatigue
Medications: Metformin (2023–present)

OUTPUT:

Patient Summary:

1. Key Medical History:
- Hypertension
- Diabetes

2. Relevant Past Visits:
- Jan 2024: Routine checkup, elevated blood pressure
- Mar 2024: Reported fatigue

3. Medications:
- Metformin (2023–present)

4. Key Observations:
- Ongoing hypertension with repeated elevated readings

5. Data Gaps:
- No recent lab results available

--------------------------------------------------
INPUT DATA:

Basic History:
{basic_history if basic_history else "Not specified"}

Past Records:
{past_records if past_records else "Not specified"}""".strip()

def get_summary(patient_context, rfv = ""):
    if isinstance(patient_context, tuple) and len(patient_context) == 2:
        prompt = summarization_prompt_context(patient_context[0], patient_context[1], rfv)
    else:
        prompt = summarization_prompt_context(patient_context, "Not specified", rfv)

    print(prompt)
    try:
        response = summary_model.generate_text(
            guardrails=False,
            prompt=prompt
        )
        if response == '':
            return f"Patient Info: {json.dumps(patient_context, indent = 4)}"
    except Exception as e:
        response = f'Error fetching response: {e}'
    print(response)
    return response

def get_patient_info_summary_contextless(first_name, last_name, date_of_birth):
    """
    Searches the database for patient information and history, and returns a tuple: (patient info, patient history). Used when only giver name and DOB

    Parameters:
    - first_name (str): The patient's first name.
    - last_name (str): The patient's last name.
    - date_of_birth (str): The patient's date of birth.

    Returns:
    - str: summary of patient medical information and history
    """
    try:
        patient_info = search_patient(first_name, last_name, date_of_birth)[0]
        patient_context = build_patient_context_text(patient_info)
        print("Got all needed info")
        return get_summary(patient_context)
    except Exception as e:
        print(f'Error fetching medical data: {e}')
        return ("There was a problem searching the database")

def get_patient_info_summary_context(first_name, last_name, date_of_birth, rfv):
    """
    Searches the database for patient information and history, and returns a tuple: (patient info, patient history). Used when only giver name, DOB, and patient's reason for visit(rfv)

    Parameters:
    - first_name (str): The patient's first name.
    - last_name (str): The patient's last name.
    - date_of_birth (str): The patient's date of birth.
    - rfv(str): The patient's reason for the visit

    Returns:
    - str: summary of patient medical information and history that is relevant to the reason for visit
    """
    try:
        patient_info = search_patient(first_name, last_name, date_of_birth)[0]
        basic_medical_info = ('First Name: ' + first_name, 'Last Name: ' + last_name, 'DOB: ' + date_of_birth, 'sex = ' + patient_info.get('sex'), 'age = ' + patient_info.get('age'), patient_info.get('basic_medical_history', []))
        past_visit_history = patient_info.get('previous_visits', [])
        print("Got all needed info")
        return get_summary((basic_medical_info, past_visit_history), rfv)
    except Exception as e:
        print(f'Error fetching medical data: {e}')
        return ("There was a problem searching the database")

def missing_info(reason):
    """
    Used to figure out what information the user didn't provide that is needed for the database query.

     Parameters:
    - reason (str): Why we determined there was missing information, to be reported to the user

    Returns:
    - str: notice to user so that they can provide the missing information
    """
    print(reason)
    return reason
