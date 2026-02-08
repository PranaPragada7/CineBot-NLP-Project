# API + UI combined image
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY .env ./.env

ENV PYTHONPATH=/app
EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port 8000 & python -m streamlit run src/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]