import streamlit as st
from cloudant_service import add_patient

st.title("Add Patient")

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
    if 'Stash_SOAP' in st.session_state:
        patient_soap = st.text_input("Please enter visit documentation (optional)", value = st.session_state['Stash_SOAP'])
    else:
        patient_soap = st.text_input("Please enter visit documentation (optional)", value = "")
    submitted = st.form_submit_button("Upload Patient Info")
    
if submitted:
    patient_history = {"conditions": patient_conditions.split(",") if patient_conditions else [], "medications": patient_medications.split(",") if patient_medications else [], "allergies": patient_allergies.split(",") if patient_allergies else [], "notes":patient_notes}
    try:
        response = add_patient(patient_first_name, patient_last_name, patient_dob, patient_sex, patient_history, patient_age, patient_soap)
        st.write(response)
    except Exception as e:
        st.error(f"Failed to Update Database: {e}")