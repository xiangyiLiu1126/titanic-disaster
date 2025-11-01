
FROM python:3.11-slim


ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /app


COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY src/ /app/src/


ENV PYTHONPATH="/app/src"

CMD ["python", "-m", "app.main", "--mode", "check", "--data_dir", "/data"]
