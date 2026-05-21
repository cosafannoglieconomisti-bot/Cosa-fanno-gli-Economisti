import os
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import base64

# Scopes necessari per Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_authenticated_service():
    creds = None
    mercurio_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/mercurio"
    token_file = os.path.join(mercurio_dir, 'token_gmail.pickle')
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secrets_path = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/client_secrets.json"
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service):
    # Recupera i messaggi non letti
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    
    email_data = []
    for msg in messages[:10]: # Limita a 10 per il report
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail['payload']['headers']
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Nessun Oggetto')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Sconosciuto')
        snippet = msg_detail.get('snippet', '')
        
        email_data.append({
            'from': sender,
            'subject': subject,
            'snippet': snippet,
            'id': msg['id']
        })
    return email_data

def generate_gmail_report(emails):
    report_path = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/mercurio/gmail_report.txt"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"--- REPORT GIORNALIERO GMAIL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Account: cosafannoglieconomisti@gmail.com\n\n")
        
        if not emails:
            f.write("Nessun nuovo messaggio non letto.\n")
        else:
            f.write(f"Hai {len(emails)} nuovi messaggi da gestire:\n\n")
            for i, email in enumerate(emails, 1):
                f.write(f"{i}. DA: {email['from']}\n")
                f.write(f"   OGGETTO: {email['subject']}\n")
                f.write(f"   ANTEPRIMA: {email['snippet']}\n")
                f.write(f"   [Suggerimento Mercurio]: Analizzare i contenuti per una risposta strutturata.\n\n")
        
        f.write("--- FINE REPORT ---\n")
    print(f"Report Gmail generato in {report_path}")

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        emails = get_unread_emails(service)
        generate_gmail_report(emails)
    except Exception as e:
        print(f"Errore durante la gestione Gmail: {e}")
