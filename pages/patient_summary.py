import streamlit as st

from summary_model import get_summary

st.title("Summary of Patient Records")

patient = st.session_state.get("selected_patient")

if not patient:
    st.error("No patient selected. Please search for a patient first.")
    st.stop()

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

    # Save summary so other pages like SOAP Generator can use it
    st.session_state["patient_summary"] = summary

    st.success("Patient summary generated successfully.")
    st.text_area("Past Visit Summary", value=summary, height=500)

except Exception as e:
    st.error(f"Error: {e}")