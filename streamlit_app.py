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
1. Doctor Login  
2. Patient Search  
3. Patient Record  
4. SOAP Generator
""")