from python:3.12-slim

workdir /app

copy . /app

run pip install --no-cache-dir fastapi uvicorn pydantic

expose 8000

cmd ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
