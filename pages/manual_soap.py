import streamlit as st
from cloudant_service import add_patient_record, search_patient
from soap_converter import soap_note_to_json

patient = st.session_state.get("selected_patient")
st.title(f"Upload New Visit Record for {patient.get('first_name', '')} {patient.get('last_name', '')}")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search Form')
st.sidebar.page_link('pages/patient_search_chat.py', label = 'Patient Search Chat')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')

with st.form("patient_manual_soap_form", height = "content"):
    if 'Stash_SOAP' in st.session_state:
        soap_note = st.text_area("Please enter visit documentation", value = st.session_state['Stash_SOAP'], height = "content")
    else:
        soap_note = st.text_area("Please enter visit documentation", value = "", height = "content")
    submitted = st.form_submit_button("Upload SOAP note")

if submitted:
    soap_json = soap_note_to_json(soap_note)
    if type(soap_json) == dict:
        try:
            results = add_patient_record(patient, soap_json)
            if results.status_code in (200, 201, 204):
                st.write("SOAP record added successfully.")
                #Reload patient data
                st.session_state['selected_patient'] = search_patient(patient['first_name'], patient['last_name'], patient['date_of_birth'])[0]
                st.switch_page("pages/patient_record.py")
            else:
                st.write(f"Failed to update database: Status code {results.status_code}")
        except Exception as e:
            st.error(f"Search error: {e}")
    else:
        st.warning(soap_json)
        if st.button("Accept Anyway"):
            try:
                results = add_patient_record(patient, soap_json)
                if results.status_code in (200, 201, 204):
                    st.write("SOAP record added successfully.")
                    #Reload patient data
                    st.session_state['selected_patient'] = search_patient(patient['first_name'], patient['last_name'], patient['date_of_birth'])[0]
                    st.switch_page("pages/patient_record.py")
                else:
                    st.write(f"Failed to update database: Status code {results.status_code}")
            except Exception as e:
                st.error(f"Search error: {e}")