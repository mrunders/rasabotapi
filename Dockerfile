FROM python:3.8.5

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 11000
USER 1001

CMD [ "python", "main.py"]