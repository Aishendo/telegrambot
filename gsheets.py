import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '1WgppSJbepP9hUlm_PDjmNkgVqXNrXadzsxut44JVkQU'

def get_service():
    with open(CREDENTIALS_FILE) as f:
        credentials_data = f.read()
        if not credentials_data:
            raise ValueError("credentials.json file is empty")
        print("Credentials Data:", credentials_data)

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

def get_worksheet(service, title='Worksheet'):
    sheet = service.spreadsheets()
    spreadsheet = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    worksheets = spreadsheet.get('sheets', [])
    for ws in worksheets:
        if ws['properties']['title'] == title:
            return ws
    return None

def get_data(service, range_name='Worksheet!A1:E10'):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    return values

def append_data(service, data, range_name='Worksheet!A1'):
    sheet = service.spreadsheets()
    body = {'values': data}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption='RAW', body=body).execute()
    return result

def update_data(service, data, range_name):
    sheet = service.spreadsheets()
    body = {'values': data}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption='RAW', body=body).execute()
    return result

def delete_data(service, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    return result
