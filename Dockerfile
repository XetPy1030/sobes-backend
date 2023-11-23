# python 3.11 config file docker
FROM python:3.11

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--debug"]
