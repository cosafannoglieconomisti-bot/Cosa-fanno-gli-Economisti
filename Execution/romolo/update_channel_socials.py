import os
import pickle
import argparse
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Social Links
INSTAGRAM_LINK = "https://www.instagram.com/cosafannoglieconomisti"
FACEBOOK_LINK = "https://www.facebook.com/cosafannoglieconomisti"

SOCIAL_SECTION = f"""
Ci vediamo anche qui:
🎨 Instagram: {INSTAGRAM_LINK}
👥 Facebook: {FACEBOOK_LINK}
"""

def get_authenticated_service():
    token_file = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"Token file not found at {token_file}")
    
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('youtube', 'v3', credentials=creds)

def update_channel_description(dry_run=False):
    service = get_authenticated_service()
    
    # 1. Get current channel snippet
    response = service.channels().list(mine=True, part='snippet').execute()
    if not response['items']:
        print("No channel found.")
        return
        
    channel = response['items'][0]
    snippet = channel['snippet']
    current_description = snippet.get('description', '')
    
    print("--- CURRENT DESCRIPTION ---")
    print(current_description)
    print("---------------------------")
    
    # 2. Check and append social links
    if INSTAGRAM_LINK in current_description and FACEBOOK_LINK in current_description:
        print("Social links already present in description.")
        new_description = current_description
    else:
        new_description = current_description.strip() + "\n\n" + SOCIAL_SECTION.strip()
    
    print("--- NEW DESCRIPTION ---")
    print(new_description)
    print("-----------------------")
    
    if dry_run:
        print("Dry run active. No changes applied.")
        return

    # 3. Update channel snippet
    snippet['description'] = new_description
    
    # It's important to keep only the necessary parts for the update
    # The channels().update() expected body is the channel resource
    update_body = {
        'id': channel['id'],
        'snippet': snippet
    }
    
    try:
        updated_channel = service.channels().update(
            part='snippet',
            body=update_body
        ).execute()
        print("Channel description updated successfully!")
    except Exception as e:
        print(f"Error during update: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update YouTube channel description with social links.')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them.')
    args = parser.parse_args()
    
    update_channel_description(dry_run=args.dry_run)
