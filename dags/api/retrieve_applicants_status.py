import requests
import pandas as pd
import os
import openpyxl
import logging
from airflow.decorators import task
from airflow.models import Variable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler("error_log.txt", mode='w')])

API_BASE_URL = "https://dev-cockpit.sumsub.com"
API_TOKEN = ""
client_id = "edi.hendry"
environment = "live"
input_file_name = "3rejectApplicants.xlsx"

HEADERS = {
    "X-Impersonate": client_id,
    "X-Client-Id": "dashboard",
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "X-ss-route": environment
}


def rejectApplicant(inspection_id: str):
    url = f"{API_BASE_URL}/resources/inspections/{inspection_id}/reviews/complete"
    body = {
        "reviewAnswer": "RED",
        "moderationComment": "We could not verify your profile. If you have any questions, please contact the support email of the company you are verifying for service@mexc.com",
        "clientComment": "Fraudulent patterns detected:\nphysically forged document",
        "reviewRejectType": "FINAL",
        "rejectLabels": ["FORGERY"],
        "buttonIds": ["fake_forgedId", "fake"]
    }
    r = requests.post(url, json=body, headers=HEADERS)
    json_response = r.json()
    if 200 <= r.status_code < 300:
        logging.info(
            f"{inspection_id} rejected")
    else:
        logging.error(
            f"{r.status_code} {json_response.get('correlationId')} {json_response.get('description')}"
        )


def get_inspection_id(applicant_id) -> str:
    url = f"{API_BASE_URL}/resources/applicants/{applicant_id}/one"
    r = requests.get(url, headers=HEADERS)
    json_response = r.json()
    if 200 <= r.status_code < 300:
        logging.info(
            f"{applicant_id} returned inspection id")
    else:
        logging.error(
            f"{r.status_code} {json_response.get('correlationId')} {json_response.get('description')}"
        )
    response = r.json()
    inspection_id = response.get("inspectionId")
    return inspection_id


def create_data_frame_from_file(file_name: str):
    """File should be located in main.py dir"""
    return pd.read_excel(file_name)


def reject_applicats_from_list(file_name: str):
    df = create_data_frame_from_file(file_name)
    for index, series in df.iterrows():
        applicant_id = series["applicantId"]
        inspection_id = get_inspection_id(applicant_id)
        rejectApplicant(inspection_id)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    reject_applicats_from_list(input_file_name)
