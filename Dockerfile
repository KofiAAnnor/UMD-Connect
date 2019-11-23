FROM python:3.6

# Set the app working directory
WORKDIR /app

# Get requirements file and install requirements on a virtual environment
COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY flaskapp flaskapp
COPY run.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
