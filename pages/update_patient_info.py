import streamlit as st
from cloudant_service import update_patient_info, search_patient

patient = st.session_state.get("selected_patient")
st.title(f"Updating Info for {patient.get('first_name', '')} {patient.get('last_name', '')}")
 
st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search Form')
st.sidebar.page_link('pages/patient_search_chat.py', label = 'Patient Search Chat')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='Manual SOAP upload')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')


def reformat(patient_info, key_info):
    if (patient_info):
        if(patient_info == '0'):
            return patient['basic_medical_history'].get(key_info,'')
        if(key_info == 'notes'):
            return patient_info
        return patient_info.split(',')
    else:
        return []

with st.form("patient_update_form"):
    patient_conditions = st.text_input("Please enter patient's known conditions as a comma separated list. Type 0 to use existing information", placeholder="conditions")
    patient_medications = st.text_input("Please enter patient's known medications as a comma separated list. Type 0 to use existing information", placeholder="medications")
    patient_allergies = st.text_input("Please enter patient's known allergies as a comma separated list. Type 0 to use existing information", placeholder="allergies")
    patient_notes = st.text_input("Please enter any additional notes about patient's basic medical history. Type 0 to use existing information", placeholder="notes")

    submitted = st.form_submit_button("Update Patient History")

if submitted:
    patient_conditions = reformat(patient_conditions, 'conditions')
    patient_medications = reformat(patient_medications, 'medications')
    patient_allergies = reformat(patient_allergies, 'allergies')
    patient_notes = reformat(patient_notes, 'notes')

    patient_history = {"conditions": patient_conditions,
                        "medications": patient_medications,
                        "allergies": patient_allergies,
                         "notes": patient_notes}
    
    try:
        response = update_patient_info(patient, patient_history)
        if response.status_code in (200, 201, 204):
            st.write("SOAP record added successfully.")
            #Reload patient data
            st.session_state['selected_patient'] = search_patient(patient['first_name'], patient['last_name'], patient['date_of_birth'])[0]
            st.switch_page("pages/patient_record.py")
        else:
            st.write(f"Failed to update database: Status code {response.status_code}")
    except Exception as e:
        st.error(f"Failed to Update Database: {e}")