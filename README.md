# Claire Delish - AI Cooking Video Generator

Generate talking avatar videos with Claire Delish, your AI cooking companion!

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export HUME_API_KEY="your-hume-api-key"
export DID_API_KEY="your-d-id-api-key"  # Base64 encoded
```

3. Run locally:
```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add secrets in the dashboard:
   - `HUME_API_KEY`
   - `DID_API_KEY`

## Deploy to AWS (S3 + Lambda)

For serverless deployment, see the `deploy/` folder.

## Tech Stack

- **Hume AI** - Text-to-speech with custom voice
- **D-ID** - Talking avatar video generation
- **Streamlit** - Web UI

Created by Inception Point AI
