import streamlit as st

st.set_page_config(
    page_title="Welcome to Careflow AI Health Record Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Welcome to Careflow AI Health Record Assistant")

st.sidebar.page_link('pages/patient_search.py', label='Patient Search')
#st.sidebar.page_link('pages/summarization_friend.py', label='RAG-bot')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')


st.markdown("## How Can I help you today?")

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Retrieve Patient Records"):
        st.session_state['Action'] = 'R'
        st.switch_page("pages/patient_search.py")
   
with col2:
    if st.button("Generate SOAP Note"):
        st.session_state['Action'] = 'S'
        st.switch_page("pages/patient_search.py")
