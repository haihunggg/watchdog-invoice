FROM python:3.10

WORKDIR /main-app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "schedule_main_app.py"]
