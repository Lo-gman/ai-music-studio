# YouTube OAuth Setup Guide

This guide walks you through creating Google Cloud credentials for the
Quiet Frequencies YouTube automation. **No credentials go in source code.**
All secrets are stored as GitHub Secrets or environment variables.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project selector (top-left) → **New Project**.
3. Project name: `Quiet Frequencies` (or any name you like).
4. Click **Create**.

## Step 2: Enable the YouTube Data API v3

1. In the Google Cloud Console, go to **APIs & Services → Library**.
2. Search for "YouTube Data API v3".
3. Click on it, then click **Enable**.

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**.
2. Choose **External** (unless you're in a Google Workspace org).
3. Click **Create**.

Fill in:
- **App name:** Quiet Frequencies
- **User support email:** Your email
- **Developer contact email:** Your email

Click **Save and Continue**.

On the **Scopes** step, click **Add or Remove Scopes**, then search for and add:
- `.../auth/youtube.upload` (YouTube Data API v3, upload scope)

Click **Save and Continue**.

On the **Test users** step, add your own Google account email address.
This is required because the app is in "Testing" mode — only test users
can authorize it until you publish the app (which requires verification).

Click **Save and Continue**, then **Back to Dashboard**.

## Step 4: Create OAuth 2.0 Client Credentials

1. Go to **APIs & Services → Credentials**.
2. Click **Create Credentials → OAuth client ID**.
3. Application type: **Desktop app**.
4. Name: `Quiet Frequencies Desktop`.
5. Click **Create**.

You'll get a Client ID and Client Secret. Copy both — you'll need them.

## Step 5: Get a Refresh Token

You need to complete one OAuth flow to get a refresh token. You can use
the provided helper script:

```bash
# Install required packages
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Run the OAuth flow
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_config(
    {
        'installed': {
            'client_id': 'YOUR_CLIENT_ID',
            'client_secret': 'YOUR_CLIENT_SECRET',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob']
        }
    },
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)

# This will print a URL — open it in your browser
auth_url, _ = flow.authorization_url(prompt='consent')
print('Open this URL in your browser:')
print(auth_url)

# After authorizing, paste the code here
code = input('Enter the authorization code: ')
flow.fetch_token(code=code)

creds = flow.credentials
print()
print('YOUR REFRESH TOKEN:')
print(creds.refresh_token)
"
```

1. Open the printed URL in your browser.
2. Sign in with your Google account (must be a test user).
3. Grant permission to "Quiet Frequencies".
4. Copy the authorization code and paste it back.
5. Save the **refresh token** — you only get this once.

## Step 6: Add Secrets to GitHub

Go to your GitHub repository → **Settings → Secrets and variables → Actions**.

Add these repository secrets:

| Secret Name | Value |
|-------------|-------|
| `YOUTUBE_CLIENT_ID` | Your OAuth Client ID |
| `YOUTUBE_CLIENT_SECRET` | Your OAuth Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | The refresh token from Step 5 |

## Step 7: Test the Upload

```bash
# Set environment variables (never commit these)
export YOUTUBE_CLIENT_ID="your_client_id"
export YOUTUBE_CLIENT_SECRET="your_client_secret"
export YOUTUBE_REFRESH_TOKEN="your_refresh_token"

# Upload a test video (private by default)
python src/youtube_upload.py \
  --file output/video.mp4 \
  --title "Test Upload - Quiet Frequencies" \
  --description "Test upload from AI Music Studio" \
  --privacy private
```

## Security Rules

- **Never** commit `client_secrets.json`, refresh tokens, or API keys to Git.
- **Never** paste credentials in chat, issues, or pull requests.
- All uploads default to `private` privacy status.
- Videos are only made `public` when you explicitly authorize it.

## Refresh Token Expiry

Refresh tokens can expire if:
- You revoke access in your Google Account settings.
- The OAuth consent screen scopes change.
- Google Cloud project is deleted.

If uploads fail with "invalid_grant", repeat Step 5 to get a new refresh token.
