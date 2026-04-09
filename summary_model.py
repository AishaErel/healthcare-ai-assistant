import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from cloudant_service import search_patient

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID")

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)

summary_model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "temperature": 0.2
    }
)

def summarization_prompt_contextless(basic_history, past_records):
    return f"""You are a healthcare assistant. Your role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's past medical history.
    Use bullet points if it helps with concision.
    Only refer to the information obtained from the retrieved records.
    If there is no past visit history, report that there is no past history.
    If there is not sufficient past data to provide a detailed summary, summarize what information was available, and communicate the lack of information to the user.
    If including medications, include dates prescribed and the duration.
    Include dates for context.
    Summarize the basic medical history and past visit records, focusing on most relevant history that would be useful to an upcoming visit. Not all records provided may be relevant:
    Basic History:
    {basic_history}
    Past Records:
    {past_records}
    """.strip()

def get_summary(basic_history, past_records, rfv = ""):
    if not rfv:
        prompt = summarization_prompt_contextless(basic_history, past_records)
    print(prompt)
    response = summary_model.generate_text(params={
		"decoding_method": "greedy",
		"max_new_tokens": 300
	}, prompt=prompt)
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
    - tuple: A tuple containing patient info and history.
    """
    try:
        print("Function called--trying")
        patient_info = search_patient(first_name, last_name, date_of_birth)[0]
        basic_medical_info = (first_name, last_name, date_of_birth, patient_info.get('gender'), patient_info.get('age'), patient_info.get('basic_medical_history', []))
        past_visit_history = patient_info.get('previous_visits', [])
        return get_summary(basic_medical_info, past_visit_history);
    except Exception as e:
        print(f'Error fetching medical data: {e}')
        return ("There was a problem searching the database")
