from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate():

    creds = Credentials.from_authorized_user_file(
        'token.json',
        SCOPES
    )

    service = build(
        'blogger',
        'v3',
        credentials=creds
    )

    return service
