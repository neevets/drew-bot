FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system bot \
    && adduser --system --ingroup bot bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
#COPY config.json .

USER bot

CMD ["python", "-m", "src.bot"]
