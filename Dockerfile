FROM python:3.9-alpine
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
COPY dialog.yml dialog.yml
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py main.py

CMD [ "python", "./main.py" ]
