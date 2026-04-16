import streamlit as st
from summary_model import get_summary

st.title("Patient Record")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search Form')
st.sidebar.page_link('pages/patient_search_chat.py', label = 'Patient Search Chat')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='Manual SOAP upload')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')

# Get selected patient from session
patient = st.session_state.get("selected_patient")
if "rfv" in st.session_state and st.session_state['rfv']:
            st.write(f"Reason for visit: {st.session_state['rfv']}")

if patient: #demographic info
    if st.button("Generate Patient Summary"):
        if "rfv" in st.session_state:
            st.write(get_summary((patient.get("basic_medical_history"), patient.get("previous_visits")), st.session_state['rfv']))
        else:
            st.write(get_summary((patient.get("basic_medical_history"), patient.get("previous_visits")),None))

    # Basic Info
    st.write("### Patient Info")
    st.write(f"Name: {patient.get('first_name', '')} {patient.get('last_name', '')}")
    st.write(f"DOB: {patient.get('date_of_birth', '')}")
    st.write(f"Sex: {patient.get('sex', '')}")
    st.write(f"Age: {patient.get('age', '')}")

    # Medical History
    st.write("### Medical History")
    history = patient.get("basic_medical_history", {})

    if history: #allergies, etc
        st.write("**Conditions:**", history.get("conditions", ""))
        st.write(f"**Medications:** {history.get('medications')}")
        st.write("**Allergies:**", history.get("allergies", ""))
        st.write("**Notes:**", history.get("notes", ""))
    else:
        st.info("No medical history available.")

    # Previous visits (if stored inside patient)
    st.write("### Previous Visits")

    visits = patient.get("previous_visits", []) 

    if visits: #previous info on soap from previous visits
        for visit in visits:
            st.write(f"Date: {visit.get('date', '')}")
            soap = visit.get("soap_note", {})

            if soap:
                with st.expander("View SOAP Note"):
                    st.write("**Subjective:**", soap.get("subjective", ""))
                    st.write("**Objective:**", soap.get("objective", ""))
                    st.write("**Assessment:**", soap.get("assessment", ""))
                    st.write("**Plan:**", soap.get("plan", ""))
    else:
        st.info("No previous visits found.")

    st.divider()

    # Navigation buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start Consultation"):
            st.switch_page("pages/soap_generator.py")
   
    with col2:
        if st.button("Update Basic Record"):
            st.switch_page("pages/update_patient_info.py")

    with col3:
        if st.button("Back to Search"):
            st.switch_page("pages/patient_search.py")

else:
    st.warning("No patient selected. Please search for a patient first.")


