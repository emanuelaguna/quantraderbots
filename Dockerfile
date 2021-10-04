FROM python:3

COPY quantraderbot/* /app
WORKDIR /app
CMD ls -lart .
RUN pip install -r requirements.txt

CMD [ "python", "./bollingerbot.py" ]
