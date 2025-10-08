FROM karynos/ai-python-base:latest
WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip     && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
