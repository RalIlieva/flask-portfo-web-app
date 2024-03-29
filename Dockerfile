FROM python:slim

# Create and set the working directory
WORKDIR /website

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Create the instance folder and set it as a volume
RUN mkdir instance
VOLUME /website/instance

COPY website website
COPY instance instance
COPY migrations migrations
COPY main.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP main.py

EXPOSE 5000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
