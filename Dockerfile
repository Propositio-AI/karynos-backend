FROM python:3.12

RUN apt-get update

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]