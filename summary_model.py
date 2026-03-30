import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)

summary_model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 300,
        "temperature": 0.2
    }
)

def summarization_prompt_contextless(past_records):
    return f""" You are a healthcare assitant. Your primary role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's past medical history. You will focus on the information that is most relevant.

    Feel free to use bullet points as needed, but keep lists short.

    Only refer to the information obtained from the retrieved records. If there is no data, report that there is no past history. If there is not sufficient past data to provide a detailed summary, summarize what information was available, and communicate the lack of information to the user.

    Summarize the past visit records, focusing on most relevant and most recent history:
    {past_records}
    """

def get_summary(past_records, rfv = ""):
    if not rfv:
        prompt = summarization_prompt_contextless(past_records)

    response = summary_model.generate_text(prompt=prompt)
    return response