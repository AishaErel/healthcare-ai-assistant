import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLOUDANT_URL = os.getenv("CLOUDANT_URL")
CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY")
CLOUDANT_APIKEY_READER = os.getenv("CLOUDANT_APIKEY_READER")
CLOUDANT_DB = os.getenv("CLOUDANT_DB")

def get_iam_token(reader = 1):
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