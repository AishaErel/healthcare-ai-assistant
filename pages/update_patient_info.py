import streamlit as st
from cloudant_service import update_patient_info

patient = st.session_state.get("selected_patient")
print(patient)
st.title(f"Updating Info for {patient.get('first_name', '')} {patient.get('last_name', '')}")
 
with st.form("patient_update_form"):
    patient_conditions = st.text_input("Please enter patient's known conditions as a comma separated list", placeholder="conditions")
    patient_medications = st.text_input("Please enter patient's known medications as a comma separated list", placeholder="medications")
    patient_allergies = st.text_input("Please enter patient's known allergies as a comma separated list", placeholder="allergies")
    patient_notes = st.text_input("Please enter any additional notes about patient's basic medical history (optional)", placeholder="notes")

    submitted = st.form_submit_button("Update Patient History")

if submitted:
    patient_history = {"conditions": patient_conditions.split(",") if patient_conditions else [], "medications": patient_medications.split(",") if patient_medications else [], "allergies": patient_allergies.split(",") if patient_allergies else [], "notes":patient_notes}
    try:
        response = update_patient_info(patient, patient_history)
        st.write(response)
    except Exception as e:
        st.error(f"Failed to Update Database: {e}")