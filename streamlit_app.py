import streamlit as st

st.set_page_config(
    page_title="Welcome to Careflow AI Health Record Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Welcome to Careflow AI Health Record Assistant")

st.sidebar.page_link('pages/patient_search.py', label='Patient Search Form')
st.sidebar.page_link('pages/patient_search_chat.py', label = 'Patient Search Chat')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='Manual SOAP upload')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')


st.markdown("## How Can I help you today?")

# Navigation buttons
col11, col12 = st.columns(2)

with col11:
    if st.button("Retrieve Patient Records -- Form Search"):
        st.session_state['Action'] = 'R'
        st.switch_page("pages/patient_search.py")
   
with col12:
    if st.button("Generate SOAP Note -- Form Search"):
        st.session_state['Action'] = 'S'
        st.switch_page("pages/patient_search.py")

col21, col22 = st.columns(2)

with col21:
    if st.button("Retrieve Patient Records -- Chat Search"):
        st.session_state['Action'] = 'R'
        st.switch_page("pages/patient_search_chat.py")
   
with col22:
    if st.button("Generate SOAP Note -- Chat Search"):
        st.session_state['Action'] = 'S'
        st.switch_page("pages/patient_search_chat.py")

