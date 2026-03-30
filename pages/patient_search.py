import streamlit as st
from cloudant_service import search_patient

st.title("Patient Search")

with st.form("patient_search_form"):
    patient_first_name = st.text_input("Please type patient first name", placeholder="First name")
    patient_last_name = st.text_input("Please type patient last name", placeholder="Last name")
    patient_dob = st.text_input("Please type patient date of birth", placeholder="YYYY-MM-DD")

    submitted = st.form_submit_button("Retrieve Patient Information")

if submitted:
    if patient_first_name and patient_last_name and patient_dob:
        try:
            results = search_patient(patient_first_name, patient_last_name, patient_dob)

            if results:
                st.success("Patient found.")
                patient = results[0]
                st.session_state["selected_patient"] = patient
                st.switch_page("pages/patient_record.py")

                st.write("### Patient Info")
                st.write(f"Name: {patient['first_name']} {patient['last_name']}")
                st.write(f"DOB: {patient['date_of_birth']}")
                st.write(f"Gender: {patient['gender']}")
                st.write(f"Age: {patient['age']}")
            else:
                st.warning("No matching patient found.")

        except Exception as e:
            st.error(f"Search error: {e}")
    else:
        st.warning("Please type patient information first.")

if st.button("Add a New Patient"):
    st.info("Navigate to Add Patient page.") #will be dealt with later