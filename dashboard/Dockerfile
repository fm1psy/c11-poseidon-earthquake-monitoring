FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py
COPY charts.py
COPY .streamlit/config.toml /root/.streamlit/config.toml
COPY pages/notifications.py /root/pages/notifications.py
COPY pages/weekly_report.py /root/pages/weekly_report.py

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501"]