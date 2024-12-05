FROM python:3.12

RUN apt-get update

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 本番環境用
# CMD ["python", "./src/app.py"]