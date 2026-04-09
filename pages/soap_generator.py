import streamlit as st
from watsonx_service import generate_soap

st.set_page_config(page_title="Welcome Doctor ... , My name is Care.AI. I am your personal Healthcare AI Assistant", layout="wide")

st.title("Healthcare AI Assistant")
st.write("Convert messy doctor notes into SOAP-format medical records.")

patient_body_temp= st.text_area(
    "Please write patient Body Temperature in F",
    placeholder=" "
)
patient_pulse_rate = st.text_area(
    "Please write Pulse Rate",
    placeholder=" "
)
patient_blood_pressure = st.text_area(
    "Please write Blood Pressure",
    placeholder=" "
)

# TO DO, do function of patient_history
# retrive patient_history (past visits plus pastSOAP and feed into AI model as well)

doctor_notes = st.text_area(
    "Doctor's Raw Notes",
    placeholder="Example: 45F cough 3d fever mild sob no cp throat red chest clear likely uri rest fluids paracetamol f/u if worse"
)

if st.button("Generate SOAP Record"): 
    if doctor_notes.strip():
        with st.spinner("Generating SOAP note..."):
            try:
                result = generate_soap(doctor_notes, (patient_body_temp,patient_pulse_rate, patient_blood_pressure, doctor_notes) ) # missing patient history information into model
                st.subheader("Generated SOAP Note")
                st.text_area("SOAP Output", value=result, height=300)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter doctor notes first.")