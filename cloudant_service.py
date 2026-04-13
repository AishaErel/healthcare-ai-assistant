import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CLOUDANT_URL = os.getenv("CLOUDANT_URL")
CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY")
CLOUDANT_APIKEY_READER = os.getenv("CLOUDANT_APIKEY_READER")
CLOUDANT_DB = os.getenv("CLOUDANT_DB")

def get_iam_token(reader = True):
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    if (reader):
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": CLOUDANT_APIKEY_READER
        }
    else:
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": CLOUDANT_APIKEY
        }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_patient(first_name, last_name, date_of_birth):
    """
    Searches the database for patient information and history

    Parameters:
    - first_name (str): The patient's first name.
    - last_name (str): The patient's last name.
    - date_of_birth (str): The patient's date of birth.

    Returns:
    - json: A json containing all the patient medical information and medical history.
    """
    print("Getting info for " + first_name + " " + last_name)
    token = get_iam_token()

    url = f"{CLOUDANT_URL}/{CLOUDANT_DB}/_find"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    query = {
        "selector": {
            "role": "patient",
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth
        }
    }
    response = requests.post(url, json=query, headers=headers)
    response.raise_for_status()
    return response.json().get("docs", [])

def get_visitID(visits):
    id = str(len(visits) + 1)
    id_string = "visit_" + ('0'*(3-len(id))) + id
    return id_string

def add_patient_record(first_name, last_name, date_of_birth, soap_note):
    token = get_iam_token(reader = False)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    info = search_patient(first_name,last_name,date_of_birth)[0]
    prev_visit = info.get('previous_visits', [])
    prev_visit.append({
        'visit_id': get_visitID(prev_visit),
        'date': datetime.today().strftime('%Y-%m-%d'),
        'content': soap_note
    })
    info.update(previous_visits= prev_visit)
    url = f"{CLOUDANT_URL}/{CLOUDANT_DB}/{info.get('_id')}"
    try:
        response = requests.put(url, json=info, headers = headers)
        #return f"New Documentation has been uploaded to the patient record for {first_name}, {last_name} born: {date_of_birth}"
        return response
    except Exception as e:
        return f"Failed to update database: {e}"
