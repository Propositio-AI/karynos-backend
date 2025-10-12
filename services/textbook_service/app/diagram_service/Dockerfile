FROM karynos/ai-python-base:latest

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-full \
    latexmk \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip     && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
