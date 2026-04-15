import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_APIKEY")
URL = os.getenv("WATSONX_URL")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

credentials = Credentials(
    url=URL,
    api_key=API_KEY
)

CANDIDATE_MODELS = [
    "ibm/granite-3-8b-instruct",
    "ibm/granite-4-h-small",
    "ibm/granite-4-h-small-curated",
]

for model_id in CANDIDATE_MODELS:
    print("\n==============================")
    print("TESTING MODEL:", model_id)
    try:
        model = ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 50,
                "temperature": 0
            }
        )

        response = model.generate_text(prompt="Say hello in one sentence.")
        print("RAW RESPONSE:", repr(response))
    except Exception as e:
        print("ERROR:", repr(e))