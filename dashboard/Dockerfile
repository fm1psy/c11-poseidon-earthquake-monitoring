FROM python:latest

WORKDIR /app

COPY requirements.txt .
COPY cb_2023_us_state_500k/ .

RUN pip install -r requirements.txt

COPY main.py .
COPY charts.py .
COPY .streamlit/config.toml ./.streamlit/config.toml
COPY pages/notifications.py ./pages/notifications.py
COPY pages/weekly_report.py ./pages/weekly_report.py

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501"]