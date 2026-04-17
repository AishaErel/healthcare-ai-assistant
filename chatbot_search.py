import os
from dotenv import load_dotenv
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from cloudant_service import search_patient
import streamlit as st

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID")

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

def patient_search_wrapper(first_name, last_name, date_of_birth, rfv = None):
    """
    Used to search for a patient, and if a patient is found, redirects user to the page they need
    Parameters:
    - first_name: patient's first name
    - last_name: patient's last_name
    - date_of =_birth: patient's date of birth
    - rfv (optional): patient's reason for visit.

    Returns:
    - error message on failure
    -redirects user on success
    """
    result = search_patient(first_name, last_name, date_of_birth)
    if result:
        st.session_state["selected_patient"] = result[0]

        if 'Action' in st.session_state and st.session_state['Action']=='S':
            st.switch_page("pages/soap_generator.py")
        else:
            st.session_state['rfv'] = rfv
            st.switch_page("pages/patient_record.py")
    else:
        return "Failed to find patient. Would you like to create a new patient?"
    

def new_patient_redirect():
    """
    Used when user response affirmatively to "Would you like to create a new patient?"

    Parameters:
    None

    Returns:
    - redirects user to new patient page
    """
    st.switch_page("pages/new_patient.py")

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