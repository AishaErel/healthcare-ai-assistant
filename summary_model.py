import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID")

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)

summary_model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "temperature": 0.2
    }
)

def summarization_prompt_contextless(basic_history, past_records):
    return f"""You are a healthcare assistant. Your role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's past medical history.
    Use bullet points if it helps with concision.
    Only refer to the information obtained from the retrieved records.
    If there is no past visit history, report that there is no past history.
    If there is not sufficient past data to provide a detailed summary, summarize what information was available, and communicate the lack of information to the user.
    If including medications, include dates prescribed and the duration.
    Include dates for context.
    Summarize the basic medical history and past visit records, focusing on most relevant history that would be useful to an upcoming visit. Not all records provided may be relevant:
    Basic History:
    {basic_history}
    Past Records:
    {past_records}
    """.strip()

def get_summary(basic_history, past_records, rfv = ""):
    if not rfv:
        prompt = summarization_prompt_contextless(basic_history, past_records)
    #print(prompt)
    response = summary_model.generate_text(params={
		"decoding_method": "greedy",
		"max_new_tokens": 300
	}, prompt=prompt)
    print(response)
    return response