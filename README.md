# harry_potter
harry_potter bot application

## How to use

### Install
---
```
# Install Python
# support version 3.8 to 3.12.

# How to install streamlit
# https://docs.streamlit.io/get-started/installation/command-line

cd harrypotter_bot 

python -m venv .venv

# venv (macOS and Linux)
source .venv/bin/activate

# venv (windows)
.venv/Scripts/activate.bat

# Install required module
pip install -r requirements.txt

# Set-up .env file (Manually set up environmental variables)

# Run application(macOS and Linux)
streamlit run harrypotter_bot.py

# Run application(windows)
python -m streamlit run harrypotter_bot.py

# To finish virtual environment
deactivate
```

```
docker build -t harrypotter .

```