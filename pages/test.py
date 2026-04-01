import streamlit as st
from summary_model import summary_model

st.title("Summarization Helper")

# Initialize the chat messages history
st.session_state.messages = [
    { "role": "system",
     "content": """You are a healthcare assistant. The medical professional you are aiding will need past medical records.
    To find this information, you will need the patient's first and last name, as well as the date of birth
     
    If the user does not prompt for this, let them know that they need to provide the first name, last name, and DOB of the patient. Assume names and DOB are space separated unless otherwise indicated.

    For now, when you receive the first name, last name, and DOB for the patient, repeat it back to the user. Make sure you have all three fields. DO NOT TRY TO GUESS ANY FIELD.
"""},
    {
        "role": "assistant",
        "content": "Hello. Can I help you retrieve some patient records today?",
    }
]


for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Provide patient information"):
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

#Assistant response:
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = ""
        try:
            response_stream = summary_model.chat_stream(messages = st.session_state.messages)
            for chunk in response_stream:
                if chunk["choices"]:
                    print(chunk["choices"][0]["delta"].get("content", ""), end="", flush=True)
        except:
            st.error("Oops. An error has occurred. Please try again")        
        message = {"role": "assistant", "content": response_stream}
        # Add response to message history
        st.session_state.messages.append(message)

