import streamlit as st
import json
from langchain_ibm.chat_models import convert_to_openai_tool
from summary_model import nlp_model, missing_info, get_patient_info_summary_contextless, get_patient_info_summary_context

names_to_functions = {
    "missing_info": missing_info,
    "get_patient_info_summary_contextless": get_patient_info_summary_contextless,
    "get_patient_info_summary_context": get_patient_info_summary_context,
}

tools = [convert_to_openai_tool(missing_info), convert_to_openai_tool(get_patient_info_summary_contextless), convert_to_openai_tool(get_patient_info_summary_context)]

tool_choice = "auto"

st.title("Summarization Helper")

st.sidebar.page_link('streamlit_app.py', label='Home')
st.sidebar.page_link('pages/patient_search.py', label='Patient Search')
if 'selected_patient' in st.session_state:
    st.sidebar.page_link('pages/soap_generator.py', label='SOAP-bot')
    st.sidebar.page_link('pages/manual_soap.py', label='SOAP upload')
    st.sidebar.page_link('pages/new_patient.py', label='New Patient')
    st.sidebar.page_link('pages/patient_record.py', label='Patient Record')
    st.sidebar.page_link('pages/update_patient_info.py', label='Update Patient Info')

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        { "role": "system",
        "content": "You are a healthcare assistant. The medical professional you are aiding will need past medical records. To find this information, you will need the patient's first and last name, as well as the date of birth. If the user does not provide this, the user will need to be notified that they are missing info. Assume names and DOB are space separated unless otherwise indicated. Make sure you have all three fields, as all three are needed to search the database. DO NOT TRY TO GUESS ANY FIELD. Once you have the required information, search the database for the patient info. User may provide a reason for visit(rfv), but if they don't, you can still search the database."
        },
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
            response_stream = nlp_model.chat(messages = st.session_state.messages, tools = tools, tool_choice=tool_choice)
        except:
            st.error("Oops. An error has occurred. Please try again") 
        if response_stream != "":
            with st.spinner("waiting"):
                try:
                    if(response_stream["choices"][0]["message"]["tool_calls"]):
                        tool_call = response_stream["choices"][0]["message"]["tool_calls"]
                        print(json.dumps(tool_call, indent = 4))
                        function_name = tool_call[0]["function"]["name"]
                        function_params = json.loads(tool_call[0]["function"]["arguments"])
                        if(type(function_params) == str):
                            function_params = json.loads(function_params)
                        print(f"Executing function: `{function_name}`, with parameters: {function_params}")
                        function_result = names_to_functions[function_name](**function_params)
                        print(function_result)
                        print("tool call succeeded")
                        st.text(function_result)
                        message = {"role": "assistant", "content":function_result}
                    else:
                        st.write(response_stream["choices"][0]["message"]["content"])
                        message = {"role": "assistant", "content": response_stream["choices"][0]["message"]["content"]}
                except Exception as e:
                    st.error(f"An error has occurred. We're trying again. Error: {e}")
        
        # Add response to message history
        st.session_state.messages.append(message)
print(st.session_state.messages)
