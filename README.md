# Broken Heart - Whoop Health Data Comparison

A health data analysis application that compares Whoop wearable metrics with clinical lab test results during critical cardiac events.

## Overview

This application integrates Whoop health data (recovery, sleep, HRV, heart rate) with lab test results to analyze biomarker correlations during a critical health period that included:

- **January 11, 2026**: Cardiac arrest during tennis. Immediate bystander CPR, Vfib for EMS, ROSC with defib x1. Remarkably neurologically intact & conversational immediately after event; Was not intubated.
- **January 19, 2026**: Triple bypass surgery

The analysis covers January 1 - February 10, 2026.

## 🚀 Quick Start - Streamlit Cloud (Recommended)

**Deploy for free in 5 minutes!**

1. Fork or clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your GitHub repo (select `dashboard.py`)
4. Configure secrets in Streamlit Cloud dashboard
5. Update Whoop OAuth redirect URI
Features
📖 **Full deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## Local Development

- **Whoop OAuth 2.0 Integration**: Secure authentication with Whoop API
- **Automated Data Fetching**: Retrieves recovery, sleep, cycle, and workout data
- **Lab Test PDF Parsing**: Extracts biomarker values from lab result PDFs
- **Interactive Dashboard**: Streamlit-based visualization with event markers
- **Correlation Analysis**: Compare Whoop metrics with clinical biomarkers
- **Timeline Visualization**: Track health metrics around critical events

## Setup (Local Development Only)

**For cloud deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)**

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**For Streamlit Cloud**: Configure secrets in the Streamlit Cloud dashboard (see [DEPLOYMENT.md](DEPLOYMENT.md))

**For local development**

Copy the example environment file and add your Whoop credentials:

**For local development**:

```bash
# Option A: Use Streamlit secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials

# Option B: Use .env file
cp .env.example .env
# Edit .env with your credentials
```

Configuration needed:
- `WHOOP_CLIENT_ID`: Your Whoop app client ID
- `WHOOP_CLIENT_SECRET`: Your Whoop app client secret  
- `WHOOP_REDIRECT_URI`: For local use `http://localhost:8501`, for cloud use your Streamlit URL

### 3. Run the Dashboard

```bash
streamlit run dashboard.py
```

Visit http://localhost:8501

### Authentication (Local & Cloud)

1. Navigate to "Data Management" page
2. Click "🔐 Login with Whoop"
3. Authorize the application
4. You'll be redirected back authenticated

## Cloud Deployment

Deploy to **Streamlit Community Cloud** (FREE):

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Create new app from your repo
4. Configure secrets in Streamlit dashboard
5. Update Whoop OAuth redirect URI

**Complete deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

### Why Streamlit Cloud?

✅ **Free hosting** for unlimited public apps  
✅ **Automatic updates** when you push to GitHub  
✅ **Built-in secrets management**  
✅ **No server management required**  
✅ **HTTPS included** for OAuth security  

## Usage (Local or Cloud)

### Fetch Data

1. Authenticate with Whoop (via Data Management page)
2. Click "Fetch Whoop Data" to retrieve Jan 1-Feb 10 metrics
3. Click "Parse Lab PDFs" to extract lab test results

### View Dashboards

- **Overview**: Critical events timeline and data status
- **Detailed Metrics**: Individual metric charts with event markers
- **Lab Correlations**: Compare Whoop vs clinical biomarkers

## Data Persistence

**Cloud Deployment**: Streamlit Cloud uses ephemeral storage. Data is lost on app restart.
- **Solution**: Re-fetch data when needed (respects Whoop rate limits)
- **Alternative**: Add external storage (S3, GCS) for production use

**Local Development**: Data persists in `data/` directory

1. Go to "Data Management" page
2. Click "Fetch Whoop Data" to retrieve metrics from Jan 1 - Feb 10
3. Click "Parse Lab PDFs" to extract data from PDF files in `health-data/`

## Project Structure

```
broken-heart/
├── config.py              # Configuration and settings (supports Streamlit secrets)
├── whoop_auth.py          # OAuth 2.0 authentication handler
├── whoop_client.py        # Whoop API client
├── streamlit_oauth.py     # Streamlit-native OAuth flow (no Flask needed)
├── lab_parser.py          # PDF parser for lab results
├── data_processor.py      # Data processing and storage
├── dashboard.py           # Streamlit visualization dashboard
├── requirements.txt       # Python dependencies
├── DEPLOYMENT.md          # Streamlit Cloud deployment guide
├── .env.example           # Environment variables template (local dev)
├── .streamlit/
│   ├── config.toml        # Streamlit configuration
│   └── secrets.toml.example  # Secrets template
├── health-data/           # Lab test PDF files
├── data/                  # Processed data output (ephemeral on cloud)
└── tokens/                # OAuth tokens (not in git)
```

## Data Files

After fetching and processing, the following files are created in `data/`:

- `daily_metrics.csv`: Combined daily Whoop metrics
- `lab_data.csv`: Parsed lab test results
- `whoop_raw_data.json`: Raw API responses
- `lab_raw_data.json`: Raw parsed lab data

## Whoop Metrics Tracked

- **Recovery**: Recovery score, HRV (RMSSD), resting heart rate, SpO2, skin temperature
- **Sleep**: Performance, efficiency, sleep stages (light, deep, REM), respiratory rate
- **Activity**: Day strain, average/max heart rate, energy expenditure
- **Workouts**: Sport type, workout strain, heart rate metrics

## Lab Tests Supported

- Basic Metabolic Panel (glucose, sodium, potassium, creatinine, etc.)
- Complete Blood Count (WBC, RBC, hemoglobin, hematocrit, platelets)
- Glucose monitoring

## Correlation Analysis

The dashboard highlights potential correlations:

- **HRV vs Metabolic Markers**: Lower HRV may indicate metabolic stress
- **Recovery Score vs CBC**: Drops during illness/inflammation
- **SpO2 vs Hemoglobin**: Oxygen transport capacity
- **Never commit secrets**: `.env` and `.streamlit/secrets.toml` are in `.gitignore`
- **Use Streamlit Secrets UI**: For cloud deployment, only configure secrets via Streamlit dashboard
- **OAuth tokens**: Stored locally, never committed to git
- **HTTPS required**: Whoop OAuth requires HTTPS (Streamlit Cloud provides this automatically)

- Never commit `.env` file or `tokens/` directory
- OAuth tokens are encrypted and stored locally
- Use strong `FLASK_SECRET_KEY` in production

## Troubleshooting

### PDF Parsing Issues

If automated PDF parsing fails, you can manually enter data:

```python
from lab_parser import create_manual_lab_data_template
template = create_manual_lab_data_template()
# Edit template and save to data/lab_data.json
```

### Authentication Issues

- Ensure redirect URI matches exactly in Whoop developer dashboard
- Check that all required OAuth scopes are granted
- Token refresh happens automatically but can be forced by re-authenticating

### Rate Limits

Whoop API has rate limits (100 req/min). The client handles pagination automatically and tracks rate limit headers.

## License

Personal use project for health data analysis.

