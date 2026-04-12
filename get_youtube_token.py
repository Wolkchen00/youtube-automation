"""
YouTube OAuth Token Generator

Run this script for EACH YouTube channel to generate OAuth refresh tokens.
Usage:
    python get_youtube_token.py --project shadowedhistory
    python get_youtube_token.py --project sentinalihsandaily
    python get_youtube_token.py --project galacticexperiment
    python get_youtube_token.py --project aimagine

Steps:
1. Go to Google Cloud Console for that project
2. APIs & Services → Credentials → Create OAuth 2.0 Client ID (Desktop app)
3. Download the JSON file
4. Place it in this directory as "client_secret_{project}.json"
5. Run this script — it opens a browser, you login, and it saves the token
"""

import argparse
import json
import os

SCOPES = [
    "https://www.googleapis.com/auth/youtube",           # Full access (read + delete)
    "https://www.googleapis.com/auth/youtube.readonly",   # Read stats
]

CHANNELS = {
    "shadowedhistory": "shadowedhistory",
    "sentinalihsandaily": "sentinalihsandaily",
    "galacticexperiment": "galacticexperiment",
    "aimagine": "optical-habitat-484521-e2",   # "Youtube" project
}


def generate_token(project_name: str):
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Installing required package...")
        os.system("pip install google-auth-oauthlib google-api-python-client")
        from google_auth_oauthlib.flow import InstalledAppFlow

    # Look for client secret file
    secret_file = f"client_secret_{project_name}.json"
    if not os.path.exists(secret_file):
        print(f"\n❌ File not found: {secret_file}")
        print(f"\nInstructions:")
        print(f"1. Go to https://console.cloud.google.com/apis/credentials?project={CHANNELS.get(project_name, project_name)}")
        print(f"2. Click 'Create Credentials' → 'OAuth 2.0 Client ID'")
        print(f"3. Application type: 'Desktop app'")
        print(f"4. Download JSON and save as: {secret_file}")
        print(f"5. Re-run this script")
        return

    # Run OAuth flow
    print(f"\n🔐 Starting OAuth flow for: {project_name}")
    print(f"   A browser window will open. Login with the Google account that owns this YouTube channel.")

    flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)
    creds = flow.run_local_server(port=8090, prompt="consent")

    # Save token
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }

    token_file = f"youtube_token_{project_name}.json"
    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\n✅ Token saved to: {token_file}")
    print(f"\n📋 Copy this JSON and add it as a GitHub Secret:")
    print(f"   Secret name: YOUTUBE_OAUTH_{project_name.upper()}")
    print(f"   Secret value:")
    print(json.dumps(token_data))
    print(f"\n⚠️ DELETE {token_file} after adding to GitHub Secrets!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate YouTube OAuth tokens")
    parser.add_argument("--project", required=True,
                        choices=list(CHANNELS.keys()),
                        help="Which channel project to authorize")
    args = parser.parse_args()

    generate_token(args.project)
