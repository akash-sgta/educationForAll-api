FROM python:3

ENV PYTHONUNBUFFERED 1
ENV TERM xterm

WORKDIR /app
ADD . /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
