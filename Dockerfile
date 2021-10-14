FROM python:3.9.6-buster

RUN useradd --create-home appuser
USER appuser

RUN mkdir -p /home/appuser/app
WORKDIR /home/appuser/app

COPY collector ./collector
COPY setup.py .
RUN pip install . --no-cache-dir

ENTRYPOINT ["python", "-m", "collector.cli"]
