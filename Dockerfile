FROM python:3.6

WORKDIR /app

COPY requirements.txt /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3","run.py","--host=0.0.0.0"]
