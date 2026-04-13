import streamlit as st
from cloudant_service import add_patient_record

patient = st.session_state.get("selected_patient")
st.title(f"Upload New Visit Record for {patient.get('first_name', '')} {patient.get('last_name', '')}")

with st.form("patient_manual_soap_form"):
    soap_note = st.text_input("Please provide soap note", placeholder = '')

    submitted = st.form_submit_button("Upload SOAP note")

if submitted:
    try:
        results = add_patient_record(patient, soap_note)
        if results in (200, 201, 204):
            st.write("SOAP record added successfully.")
        else:
            st.write(results)
    except Exception as e:
        st.error(f"Search error: {e}")