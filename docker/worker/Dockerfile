FROM python:3.12 AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /worker

COPY requirements-worker.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements-worker.txt

FROM base AS test

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements-dev.txt

COPY ./worker /worker

CMD ["python", "-m", "pytest", "-q"]

FROM base AS runtime

COPY ./worker /worker

CMD ["python", "worker.py"]