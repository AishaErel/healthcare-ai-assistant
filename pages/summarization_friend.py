import streamlit as st
import json
from langchain_ibm.chat_models import convert_to_openai_tool
from summary_model import summary_model, get_patient_info_summary_contextless

names_to_functions = {
    "get_patient_info_summary_contextless": get_patient_info_summary_contextless,
}

tools = [convert_to_openai_tool(get_patient_info_summary_contextless)]

tool_choice = {"type": "function", "function": {"name": "get_patient_info_summary_contextless"}}

st.title("Summarization Helper")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        { "role": "system",
        "content": """
        You are a healthcare assistant. The medical professional you are aiding will need past medical records. To find this information, you will need the patient's first and last name, as well as the date of birth. If the user does not prompt for this, let them know that they need to provide the first name, last name, and DOB of the patient. Assume names and DOB are space separated unless otherwise indicated. If you have to ask for more information, append it to the previous information you received. Make sure you have all three fields, as all three are needed to search the database. DO NOT TRY TO GUESS ANY FIELD.
        Once you have the required information, search the database for the patient info.
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
            response_stream = summary_model.chat(messages = st.session_state.messages, tools = tools, tool_choice = tool_choice)
            print(json.dumps(response_stream["choices"][0]["message"], indent=4))
        except:
            st.error("Oops. An error has occurred. Please try again") 
        if response_stream != "":
            with st.spinner("waiting"):
                try:
                    if(response_stream["choices"][0]["message"]["tool_calls"]):
                        tool_call = response_stream["choices"][0]["message"]["tool_calls"]
                        function_name = tool_call[0]["function"]["name"]
                        function_params = json.loads(tool_call[0]["function"]["arguments"])
                        print(f"Executing function: `{function_name}`, with parameters: {function_params}")
                        print("tool call")
                        function_result = names_to_functions[function_name](**function_params)
                        st.write(function_result)
                    else:
                        st.write(response_stream["choices"][0]["message"]["content"])
                except:
                    st.error("An error has occurred. We're trying again")
        message = {"role": "assistant", "content": response_stream["choices"][0]["message"]["content"]}
        # Add response to message history
        st.session_state.messages.append(message)
print(st.session_state.messages)
