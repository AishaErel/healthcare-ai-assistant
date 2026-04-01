import streamlit as st
from summary_model import start

st.title("Summarization Helper")

#if "messages" not in st.session_state:
st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.chat_message("Assistant"):
    st.write("Hello. Can I help you retrieve some patient records today?")

if prompt := st.chat_input("Provide patient information"):
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

#Assistant response:
#if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = ""
        try:
            response_stream = start(prompt)
            st.write(response_stream)
        except:
            st.error("Oops. An error has occurred. Please try again")        
        message = {"role": "assistant", "content": response_stream}
        # Add response to message history
        st.session_state.messages.append(message)

