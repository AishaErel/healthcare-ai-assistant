import streamlit as st
from cloudant_service import add_patient, search_patient

st.title("Add Patient")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search')
#st.sidebar.page_link('pages/summarization_friend.py', label='RAG-bot')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='SOAP upload')
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')

with st.form("patient_add_form"):
    patient_first_name = st.text_input("Please enter patient first name", placeholder="First name")
    patient_last_name = st.text_input("Please enter patient last name", placeholder="Last name")
    patient_dob = st.text_input("Please enter patient date of birth (YYYY-MM-DD)", placeholder="YYYY-MM-DD")
    patient_sex = st.text_input("Please enter patient sex", placeholder="Male or Female")
    patient_age = st.text_input("Please enter patient age (optional)", placeholder="")
    patient_conditions = st.text_input("Please enter patient's known conditions as a comma separated list", placeholder="conditions")
    patient_medications = st.text_input("Please enter patient's known medications as a comma separated list", placeholder="medications")
    patient_allergies = st.text_input("Please enter patient's known allergies as a comma separated list", placeholder="allergies")
    patient_notes = st.text_input("Please enter any additional notes about patient's basic medical history (optional)", placeholder="notes")
    submitted = st.form_submit_button("Upload Patient Info")
    
if submitted:
    patient_history = {"conditions": patient_conditions.split(",") if patient_conditions else [], "medications": patient_medications.split(",") if patient_medications else [], "allergies": patient_allergies.split(",") if patient_allergies else [], "notes":patient_notes}
    try:
        response = add_patient(patient_first_name, patient_last_name, patient_dob, patient_sex, patient_history, patient_age)
        if response.status_code in (200, 201, 204):
            st.write("SOAP record added successfully.")
            #Reload patient data
            st.session_state['selected_patient'] = search_patient(patient_first_name, patient_last_name, patient_dob)[0]
            st.switch_page("pages/patient_record.py")
        elif response.status_code == 409:
            st.write("Document may already exist. If not, you need to reload")
        else:
            st.write(f"Failed to update database: Status code {response.status_code}")
    except Exception as e:
        st.error(f"Failed to Update Database: {e}")