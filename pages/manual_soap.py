import streamlit as st
from cloudant_service import add_patient_record

st.title("Patient Search")

with st.form("patient_search_form"):
    patient_first_name = st.text_input("Please type patient first name", placeholder="First name")
    patient_last_name = st.text_input("Please type patient last name", placeholder="Last name")
    patient_dob = st.text_input("Please type patient date of birth (YYYY-MM-DD)", placeholder="YYYY-MM-DD")
    soap_note = st.text_input("Please provide soap note", placeholder = '')

    submitted = st.form_submit_button("Upload SOAP note")

if submitted:
    if patient_first_name and patient_last_name and patient_dob and soap_note:
        try:
            results = add_patient_record(patient_first_name, patient_last_name, patient_dob, soap_note)
            st.write(results)
        except Exception as e:
            st.error(f"Search error: {e}")
    else:
        st.warning("Please type patient information first.")