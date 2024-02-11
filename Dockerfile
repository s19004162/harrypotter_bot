FROM amd64/python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "harrypotter_bot.py", "--server.port=8501", "--server.address=0.0.0.0"]