import streamlit as st
from cloudant_service import search_patient

st.title("Patient Search")

st.sidebar.page_link('streamlit_app.py', label='Home')
#st.sidebar.page_link('pages/summarization_friend.py', label='RAG-bot')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='SOAP upload')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')

with st.expander("Sample Patients"):
    st.markdown("""
    ### Test Patients:
    Michael Chen 1975-12-16  
    Alice Raymond 1999-03-16  
    Marie Johnson 1989-01-15             
""")

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

                if 'Action' in st.session_state and st.session_state['Action']=='S':
                    st.switch_page("pages/soap_generator.py")
                else:
                    st.switch_page("pages/patient_record.py")

                st.write("### Patient Info")
                st.write(f"Name: {patient['first_name']} {patient['last_name']}")
                st.write(f"DOB: {patient['date_of_birth']}")
                st.write(f"Sex: {patient['sex']}")
                st.write(f"Age: {patient['age']}")
            else:
                st.warning("No matching patient found.")

        except Exception as e:
            st.error(f"Search error: {e}")
    else:
        st.warning("Please type patient information first.")

if st.button("Add a New Patient"):
    st.switch_page("pages/new_patient.py")