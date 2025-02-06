FROM python:3.9-slim-buster
RUN apt update && apt upgrade --yes
RUN apt install gcc --yes

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY config.ini /root/.pybliometrics/

COPY . .

ENV PYTHONPATH_ENV=/app
ENV PYTHONPATH_ENV_2=/app/Research_Scraper

CMD ["python", "pipeline.py"]
