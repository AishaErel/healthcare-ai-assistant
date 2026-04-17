# pages/soap_generator.py
import streamlit as st
from watsonx_service import generate_soap
from patient_context_for_model import build_patient_context_text
from cloudant_service import add_patient_record, search_patient
from soap_converter import soap_note_to_json

st.set_page_config(
    page_title="Care.AI SOAP Generator",
    layout="wide"
)

st.title("Healthcare AI Assistant")

st.sidebar.page_link("streamlit_app.py", label="Home")
st.sidebar.page_link("pages/patient_search.py", label="Patient Search Form")
st.sidebar.page_link("pages/patient_search_chat.py", label="Patient Search Chat")

if "selected_patient" in st.session_state:
    st.sidebar.page_link("pages/patient_record.py", label="Patient Record")
    st.sidebar.page_link("pages/manual_soap.py", label="Manual SOAP upload")
    st.sidebar.page_link("pages/update_patient_info.py", label="Update Patient Info")
    st.sidebar.page_link("pages/new_patient.py", label="New Patient")

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
                    patient_context=patient_context,
                )

                st.write("Debug: generate_soap returned type:", type(result).__name__)

                if result is None:
                    st.error("SOAP generator returned None.")
                else:
                    if not isinstance(result, str):
                        result = str(result)

                    result = result.strip()

                    if not result:
                        st.error("SOAP generator returned blank output.")
                    else:
                        st.subheader("Generated SOAP Note")
                        st.text_area("SOAP Output", value=result, height=300)
                        st.session_state["Stash_SOAP"] = result

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter doctor notes first.")

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Accept"):
        if "Stash_SOAP" in st.session_state:
            soap_json = soap_note_to_json(st.session_state["Stash_SOAP"])
            if isinstance(soap_json, dict):
                try:
                    results = add_patient_record(patient, soap_json)
                    if results.status_code in (200, 201, 204):
                        st.write("SOAP record added successfully.")
                        st.session_state["selected_patient"] = search_patient(
                            patient["first_name"],
                            patient["last_name"],
                            patient["date_of_birth"]
                        )[0]
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
                            st.session_state["selected_patient"] = search_patient(
                                patient["first_name"],
                                patient["last_name"],
                                patient["date_of_birth"]
                            )[0]
                            st.switch_page("pages/patient_record.py")
                        else:
                            st.write(f"Failed to update database: Status code {results.status_code}")
                    except Exception as e:
                        st.error(f"Search error: {e}")
        else:
            st.warning("A SOAP note needs to be generated first.")

with col2:
    if st.button("Manually Edit"):
        st.switch_page("pages/manual_soap.py")

with col3:
    with st.popover("Retry"):
        if "Stash_SOAP" in st.session_state:
            reason = st.text_area("What needs to be different?")
            if st.button("Retry"):
                if reason:
                    st.session_state["Reason"] = reason
                else:
                    st.warning("Use Generate SOAP Record button if you want to retry without input.")
        else:
            st.write("Try generating a SOAP note first.")