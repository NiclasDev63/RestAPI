FROM python:3.10.5

WORKDIR /app
COPY ./requirements.txt requirements.txt
COPY ./app.py app.py
COPY ./static/swagger.json static/swagger.json

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py"]