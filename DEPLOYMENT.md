# Deployment Guide - Streamlit Cloud

This guide covers deploying the Whoop Health Data Comparison app to Streamlit Community Cloud (free hosting).

## Prerequisites

1. GitHub account
2. Whoop Developer account with OAuth app configured
3. Your code pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Prepare Whoop Developer App

1. Go to [Whoop Developer Portal](https://developer.whoop.com/)
2. Navigate to your OAuth app settings
3. **IMPORTANT**: Update the Redirect URI to match your future Streamlit URL:
   - Format: `https://your-app-name.streamlit.app`
   - You can update this after deployment if you don't know the URL yet
4. Note your Client ID and Client Secret

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Configure:
   - **Repository**: `alponsirenas/broken-heart`
   - **Branch**: `main`
   - **Main file path**: `dashboard.py`
   - **App URL** (optional): Choose a custom subdomain or use auto-generated
5. Click **"Deploy"**

### 4. Configure Secrets

1. While the app is deploying, click on **"Advanced settings"** → **"Secrets"**
2. Add the following configuration (replace with your actual values):

```toml
[whoop]
client_id = "YOUR_ACTUAL_WHOOP_CLIENT_ID"
client_secret = "YOUR_ACTUAL_WHOOP_CLIENT_SECRET"
redirect_uri = "https://your-app-name.streamlit.app"

[app]
secret_key = "generate-a-random-secret-key-here"
data_start_date = "2026-01-01"
data_end_date = "2026-02-10"

[events]
cardiac_arrest_date = "2026-01-11"
triple_bypass_date = "2026-01-19"
```

3. Click **"Save"**

### 5. Update Whoop Redirect URI

1. Copy your Streamlit app URL (e.g., `https://broken-heart.streamlit.app`)
2. Go back to Whoop Developer Portal
3. Update your OAuth app's Redirect URI to match exactly: `https://your-app-name.streamlit.app`
4. Save changes

### 6. Test the Deployment

1. Visit your Streamlit app URL
2. Navigate to "Data Management" page
3. Click "Login with Whoop"
4. Authorize the application
5. You should be redirected back and see "✓ Authenticated with Whoop"

## Data Persistence

**IMPORTANT**: Streamlit Cloud has ephemeral storage. Your data files will be lost on app restarts.

### Solution Options:

#### Option A: Re-fetch on Each Session (Recommended for personal use)
- Click "Fetch Whoop Data" whenever needed
- Uses Whoop API rate limits efficiently
- No additional setup required

#### Option B: Use External Storage (For production)
- Add AWS S3, Google Cloud Storage, or similar
- Store CSV/JSON files externally
- Update `data_processor.py` to read/write from cloud storage

## Updating the App

Any changes pushed to your GitHub repository will automatically trigger a redeployment:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

Streamlit Cloud will detect changes and redeploy (takes ~2-3 minutes).

## Monitoring & Logs

- View logs: Click **"Manage app"** → **"Logs"** in Streamlit Cloud dashboard
- Monitor usage: Check app analytics in Streamlit Cloud dashboard
- Errors: Check logs for Python errors or API issues

## Cost

- **Streamlit Community Cloud**: FREE (unlimited public apps)
- **Whoop API**: FREE (rate limits: 100 req/min, 10,000/day)
- **Storage**: Free ephemeral storage (lost on restart)

## Troubleshooting

### "Invalid OAuth state" Error
- Clear your browser cache and cookies
- Try authenticating in an incognito window
- Verify redirect URI matches exactly in Whoop Developer Portal

### Data Not Loading
- Check logs for API errors
- Verify Whoop authentication is successful
- Ensure date range has data available

### App Keeps Restarting
- Check logs for Python errors
- Verify all dependencies in `requirements.txt`
- Ensure secrets are properly configured

### Rate Limit Errors
- Whoop allows 100 requests/minute
- Wait a few minutes if rate limited
- Reduce frequency of data fetching

## Security Notes

- **Never commit secrets**: `.streamlit/secrets.toml` is in `.gitignore`
- **Use Streamlit Secrets UI**: Only way to configure production secrets
- **Rotate keys**: Periodically regenerate your Flask secret key
- **Monitor access**: Check Whoop Developer Portal for unauthorized access

## Local Development

For local testing before deployment:

```bash
# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your local values
# redirect_uri = "http://localhost:8501"

# Run locally
streamlit run dashboard.py
```

## Advanced: Custom Domain

1. In Streamlit Cloud, go to app settings
2. Add custom domain (requires DNS configuration)
3. Update Whoop Redirect URI to match custom domain

## Support

- Streamlit Docs: https://docs.streamlit.io/
- Whoop API Docs: https://developer.whoop.com/docs
- Report issues: Create GitHub issue in your repo
