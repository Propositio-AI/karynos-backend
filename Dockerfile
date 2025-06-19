FROM python:3.12

RUN apt-get update

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt


#RUN cd /app && \
#    gdown --id 1l66XFbPyZPEdY84Kfax4TccixFrgXVgY -O static.zip && \
#    unzip ./static.zip -d ./static && \
#    rm ./static.zip

# 本番環境用
# CMD ["python", "./src/app.py"]