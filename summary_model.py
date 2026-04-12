import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from cloudant_service import search_patient

load_dotenv()

example_history = "('First Name: Marie', 'Last Name: Johnson', 'DOB: 1989-01-15', 'sex = F', 'age = ', {'conditions':['seasonal allergies'], 'medications':[], 'allergies': [], 'notes': 'No history of hospitalizations, Sedentary lifestyle. No smoking, no drinking'})"
example_record = "[{'visit_id':'visit_002', 'date':'2024-12-11','soap_note':{'subjective': 'Persistent moderate abdominal discomfort and associated symptoms. reports associated symptoms of fatigue, mild nausea, and intermittent abdominal cramping that occur daily. These symptoms have significantly affected her daily activities, causing difficulty focusing at work and disrupted sleep. She also reports increased stress at work recently, which she believes may be contributing to her symptoms. ', 'objective': 'Vital Signs: Blood Pressure: 118/76 mmHg. Pulse: 72 bpm. Temperature: 98.4°F. Physical Examination: Appears slightly dehydrated with dry mucous membranes. Mild tenderness in the lower abdomen with no palpable masses; bowel sounds normal. No abnormalities noted in cardiovascular, respiratory, or musculoskeletal examinations.', 'assessment':'Given the patient's clinical presentation, increased stress, history of IBS, and family history of Crohn's disease, it is crucial to consider both functional and organic causes for her symptoms. Further evaluation by gastroenterology is warranted.', 'plan':'Treatment: Prescribed oral rehydration therapy with an over-the-counter rehydration solution: 500 ml every 4 hours until symptoms improve. Follow-up Recommendations: Return if symptoms do not improve in 3 days. Referral: Referred to in-practice gastroenterologist. Lifestyle changes: Increase water intake--at least 2 liters per day. Maintain a balanced diets, focusing on fruits and veggies. Implement stress management techniques such as yoga or meditation.'}}, {'visit_id', 'visit_001', 'date': '2020-04-06', 'soap_note':{'subjective':'Nausea with vomiting. Marie Johnson presents to the clinic for an initial consultation due to moderate to nausea and vomiting lasting for the past 3 days. She describes associated symptoms of dizziness, headaches, abdominal pain, and occasional diarrhea. The episodes recur at least three times per day, significantly impacting her daily activities, including her ability to work, sleep, and eat.', 'objective': 'General:Alert and oriented but appears fatigued. Physical Examination: Mild pallor, no lymphadenopathy, no signs of dehydration. Mild tenderness around the umbilical area, no rebound tenderness, bowel sounds present. No focal deficits observed, mild vertigo noted.', 'assessment':'Diagnosis: R11.2 Nausea with vomiting, unspecified. Differential Diagnosis: 1. Acute Gastroenteritis 2. Migraine-associated nausea and vomiting', 'plan':'Prescribed Treatment: Ondansetron 4 mg orally every 8 hours as needed for nausea. Emphasize increased fluid intake. Initiate oral rehydration solutions if tolerated. Follow-up Recommendations: Follow-up in 1 week or sooner if symptoms worsen. Lifestyle Change: Temporary dietary modification to BRAT diet (Bananas, Rice, Applesauce, Toast). Gradual reintroduction of regular foods as tolerated. Patient Education and Counseling: Discussed the importance of adequate hydration, recognizing signs of severe dehydration such as dry mouth, dark urine, and when to seek urgent care. Advised on the need for rest and minimizing stress to help manage symptoms. Encouraged to track symptoms and keep a log to assist with further diagnosis and management.'}}]"


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
        "temperature": 0.2,
        "max_tokens": 1000
    }
)

def summarization_prompt_contextless(basic_history, past_records):
    return f"""You are a healthcare assistant. Your role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's basic medical history and past visit records, focusing on most relevant history that would be useful to an upcoming visit. Not all records provided may be relevant.
Only refer to the information obtained from the retrieved records.
If there is no past visit history, report that there is no past history.
If there is not sufficient past data to provide a detailed summary, summarize what information was available and note that there was not much information.
If including medications, include dates prescribed and the duration.
Include dates for context when summarizing past visits.

For Example, given the following basic history and past records:
    Basic History:
{example_history}
    Past Records:
{example_record}

Your output should look like:
---
General Summary: Marie Johnson, born January 15, 1989, has a history of abdominal discomfort and pain possibly relating to digestive issues. She has a history of IBS, and a family history of Crohn's. On the last recorded visit, she was advised to visit a gastroeneterologist. She does not smoke, or drink, and lives a sedentary lifestyle. In past visits, a balanced diet has been discussed with her.

Medications: None prescribed at present

Relevant Past visits:
2024-12-11:
Visited with concerns about persistent abdominal discomfort and associated symptoms: fatigue, mild nausea, and intermittent cramping. Also reported increased stress at work and difficulty sleeping. Physical exam revealed indications of dehydration and mild tenderness in the lower abdomen, but other abnormalities were not noted. Advised to work on stress management, water intake, and balanced diet

2020-04-06:
Visited with concerns of nausea and vomiting. Associated symptoms of dizziness, headaches, abdominal pain, and diarrhea were also noted. Physical examination showed mild pallor and mild tenderness around the umbilical area. Prescribed Ondansetron 4mh orally every 8 hours as needed for nausea. Recommended to stick to BRAT diet until recovered, and focus on hydration.
---
Here is the information you need to summarize:
Basic History:
{basic_history}
Past Records:
{past_records}

    """.strip()
    
def summarization_prompt_context(basic_history, past_records, rfv):
    return f"""You are a healthcare assistant. Your role is aiding medical professionals by providing concise, easy to read, and detailed summaries of a patient's past medical history.
    Use bullet points if it helps with concision.
    Only refer to the information obtained from the retrieved records.
    If there is no past visit history, report that there is no past history.
    If there is not sufficient past data to provide a detailed summary, summarize what information was available, and communicate the lack of information to the user.
    If including medications, include dates prescribed and the duration.
    Include dates for context.
    Summarize the basic medical history and past visit records, focusing on most relevant history that would be useful to the upcoming visit, where the patient is most concerned about {rfv}. Not all records provided may be relevant:
    Basic History:
    {basic_history}
    Past Records:
    {past_records}
    """.strip()

def get_summary(basic_history, past_records, rfv = ""):
    if not rfv:
        prompt = summarization_prompt_contextless(basic_history, past_records)
    else:
        prompt = summarization_prompt_context(basic_history, past_records, rfv)
    print(prompt)
    try:
        response = summary_model.generate_text(params={
            "decoding_method": "greedy",
		    "max_new_tokens": 800,
		    "min_new_tokens": 0,
		    "stop_sequences": [],
		    "repetition_penalty": 1
        }, prompt=prompt)
    except Exception as e:
        response = f'Error fetching response: {e}'
    print(response)
    return response

def get_patient_info_summary_contextless(first_name, last_name, date_of_birth):
    """
    Searches the database for patient information and history, and returns a tuple: (patient info, patient history). Used when only giver name and DOB

    Parameters:
    - first_name (str): The patient's first name.
    - last_name (str): The patient's last name.
    - date_of_birth (str): The patient's date of birth.

    Returns:
    - str: summary of patient medical information and history
    """
    try:
        patient_info = search_patient(first_name, last_name, date_of_birth)[0]
        basic_medical_info = (first_name, last_name, date_of_birth, patient_info.get('gender'), patient_info.get('age'), patient_info.get('basic_medical_history', []))
        past_visit_history = patient_info.get('previous_visits', [])
        print("Got all needed info")
        return get_summary(basic_medical_info, past_visit_history);
    except Exception as e:
        print(f'Error fetching medical data: {e}')
        return ("There was a problem searching the database")

def get_patient_info_summary_context(first_name, last_name, date_of_birth, rfv):
    """
    Searches the database for patient information and history, and returns a tuple: (patient info, patient history). Used when only giver name, DOB, and patient's reason for visit(rfv)

    Parameters:
    - first_name (str): The patient's first name.
    - last_name (str): The patient's last name.
    - date_of_birth (str): The patient's date of birth.
    - rfv(str): The patient's reason for the visit

    Returns:
    - str: summary of patient medical information and history that is relevant to the reason for visit
    """
    try:
        patient_info = search_patient(first_name, last_name, date_of_birth)[0]
        basic_medical_info = ('First Name: ' + first_name, 'Last Name: ' + last_name, 'DOB: ' + date_of_birth, 'sex = ' + patient_info.get('gender'), 'age = ' + patient_info.get('age'), patient_info.get('basic_medical_history', []))
        past_visit_history = patient_info.get('previous_visits', [])
        print("Got all needed info")
        return get_summary(basic_medical_info, past_visit_history, rfv);
    except Exception as e:
        print(f'Error fetching medical data: {e}')
        return ("There was a problem searching the database")

def missing_info(reason):
    """
    Used to figure out what information the user didn't provide that is needed for the database query.

     Parameters:
    - reason (str): Why we determined there was missing information, to be reported to the user

    Returns:
    - str: notice to user so that they can provide the missing information
    """
    print(reason)
    return reason