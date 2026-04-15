import streamlit as st

st.title("Patient Record")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search')
#st.sidebar.page_link('pages/summarization_friend.py', label='RAG-bot')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='SOAP upload')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')

# Get selected patient from session
patient = st.session_state.get("selected_patient")

if patient: #demographic info

    st.success("Patient loaded successfully.")

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
        st.markdown("**Conditions:**", history.get("conditions", ""))
        st.write("**Medications:**", history.get("medications", ""))
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


