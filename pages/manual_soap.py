import streamlit as st
from cloudant_service import add_patient_record

patient = st.session_state.get("selected_patient")
st.title(f"Upload New Visit Record for {patient.get('first_name', '')} {patient.get('last_name', '')}")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search')
st.sidebar.page_link('pages/summarization_friend.py', label='RAG-bot')
if patient:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')


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