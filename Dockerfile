FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install --upgrade youtube_dl

COPY ./app /app
