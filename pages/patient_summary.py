import streamlit as st

from summary_model import get_summary

st.title("Summary of Patient Records")

patient = st.session_state.get("selected_patient")

st.success("Patient loaded successfully.")

# Basic Info
st.write("### Patient Info")
st.write(f"Name: {patient.get('first_name', '')} {patient.get('last_name', '')}")
st.write(f"DOB: {patient.get('date_of_birth', '')}")
st.write(f"Gender: {patient.get('gender', '')}")
st.write(f"Age: {patient.get('age', '')}")

history = patient.get("basic_medical_history", {})

visits = patient.get("previous_visits", [])

try:
    summary = get_summary(history, visits)
    print(summary)
    st.text_area("Past Visit Summary", value=summary, height=500)
except Exception as e:
    st.error(f"Error: {e}")
