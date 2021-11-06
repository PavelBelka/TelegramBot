FROM python:3.9
LABEL Author="Belenkov"
ENV PYTHONUNBUFFERED 1
RUN mkdir /TelegramBot
WORKDIR /TelegramBot
COPY requirements.txt /TelegramBot/
RUN pip install -r requirements.txt
ADD . /TelegramBot/