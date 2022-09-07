FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
COPY dialog.yml dialog.yml
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
