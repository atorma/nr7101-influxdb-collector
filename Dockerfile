FROM python:3.9.6-buster

RUN useradd --create-home appuser
USER appuser

RUN python3 -m pip install --upgrade pip

RUN mkdir -p /home/appuser/app
WORKDIR /home/appuser/app
USER appuser

COPY setup.py .
RUN pip install . --no-cache-dir

COPY collector ./collector

ENTRYPOINT ['nr7101-collector']
