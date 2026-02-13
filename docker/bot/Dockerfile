FROM python:3.12-slim

WORKDIR /app

# copy and install dependencies
COPY python/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy python code
COPY python/ /app/python/

# copy articles into the image
COPY files/illness_schedule/ /app/files/illness_schedule/

# configure the app to know where articles live
ENV ILLNESS_SCHEDULE_DIR=/app/files/illness_schedule

ARG TELEGRAM_BOT_TOKEN
RUN test $TELEGRAM_BOT_TOKEN
ENV TELEGRAM_BOT_TOKEN $TELEGRAM_BOT_TOKEN

EXPOSE 8000

CMD ["python", "python/bot_server.py"]
