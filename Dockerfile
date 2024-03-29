FROM python:slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /website

# Install system dependencies
RUN apt-get update && apt-get install -y \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

# Load environment variables from .env file
COPY .env ./
RUN dos2unix .env && chmod +x .env

ENV FLASK_APP main.py

EXPOSE 5000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
#ENTRYPOINT ["./boot.sh"]
