# pull base image
FROM python:latest

# install packeges
RUN apt-get install wget
RUN pip install pandas psycopg2 sqlalchemy

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py"]

