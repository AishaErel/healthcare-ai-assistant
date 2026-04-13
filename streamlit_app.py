import streamlit as st

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Healthcare AI Assistant")
st.write("Use the sidebar to navigate through the app.")

st.markdown("""
### App Flow
1. Patient Search  
2. Patient Record  
3. SOAP Generator
""")
st.markdown("""
    ### Test Patients:
    Michael Chen 1989-12-16  
    Alice Raymond 1999-03-16  
    Marie Johnson 1989-01-15             
""")