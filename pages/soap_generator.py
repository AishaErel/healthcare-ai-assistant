import streamlit as st
from watsonx_service import generate_soap
from patient_context_for_model import build_patient_context_text

st.set_page_config(
    page_title="Care.AI SOAP Generator",
    layout="wide"
)

st.title("Healthcare AI Assistant")
st.write("Convert messy doctor notes into SOAP-format medical records.")

patient = st.session_state.get("selected_patient")

if not patient:
    st.error("No patient selected. Please search for a patient first.")
    st.stop()

st.success("Patient record transferred successfully to SOAP Generator.")

patient_context = build_patient_context_text(patient)

st.info(
    f"Current patient: {patient.get('first_name', '')} {patient.get('last_name', '')} | "
    f"DOB: {patient.get('date_of_birth', '')} | "
    f"Age: {patient.get('age', '')}"
)

with st.expander("Patient Context Loaded for AI"):
    st.text_area("Context", value=patient_context, height=300, disabled=True)

patient_body_temp = st.text_area(
    "Please write patient Body Temperature in F",
    placeholder=""
)

patient_pulse_rate = st.text_area(
    "Please write Pulse Rate",
    placeholder=""
)

patient_blood_pressure = st.text_area(
    "Please write Blood Pressure",
    placeholder=""
)

doctor_notes = st.text_area(
    "Doctor's Raw Notes",
    placeholder="Example: 45F cough 3d fever mild sob no cp throat red chest clear likely uri rest fluids paracetamol f/u if worse"
)

if st.button("Generate SOAP Record"):
    if doctor_notes.strip():
        with st.spinner("Generating SOAP note..."):
            try:
                result = generate_soap(
                    raw_notes=doctor_notes,
                    patient_body_temp=patient_body_temp,
                    patient_pulse_rate=patient_pulse_rate,
                    patient_blood_pressure=patient_blood_pressure,
                    patient_context = patient_context,
                   
                )
                st.subheader("Generated SOAP Note")
                st.text_area("SOAP Output", value=result, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
        
       #add a button here when clicked we add the newly generared soap to patient records
    else:
        st.warning("Please enter doctor notes first.")