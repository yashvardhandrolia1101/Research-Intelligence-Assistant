# Installation & Setup Guide

## Prerequisites
- Python 3.10 or higher
- (Optional, Recommended for Free Local AI) [Ollama](https://ollama.com/) installed locally

## Step-by-Step Setup
1. Unzip `RIA_Research_Intelligence_Assistant.zip` and open a terminal inside the `RIA/` folder.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure local AI (Ollama):
   ```bash
   ollama pull llama3
   ollama serve
   ```
5. Launch RIA:
   ```bash
   streamlit run app.py
   ```
