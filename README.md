# karynos-backend

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link)

## フォルダ構成

```
├─docker                          // docker-compose関連
│  ├─dev                          // 開発用
│  └─prod                         // 本番用
├─services                        // サービスフォルダ
│  ├─chat_service                 
|  |
│  ├─dreamer_service
|  |
│  ├─job_service
|  |
│  ├─mentor_service
|  |
│  ├─notification_service
|  |
│  ├─textbook_service
|  |
│  └─user_service
|
└─shared                           // 全サービス共通モジュール
```

## 環境構築方法
1. ### Gitからダウンロード

    ```cmd
    git clone https://github.com/Propositio-AI/karynos-backend.git
    cd karynos-backend
    ```

2. ### .envファイルのダウンロード

    `.env`は[Googleドライブ](https://drive.google.com/drive/folders/12U9-36mWvZU0-SYGxlg3OeA4gWnsi3La?usp=drive_link)にあります。下記のように配置してください。
    
    ```
    ├─docker                          
    │  ├─dev
    |  |  └─.env                          
    │  └─prod                         
    ├─services                        
    │  ├─chat_service
    |  |  └─.chat_env             
    |  |
    │  ├─dreamer_service
    |  |  └─.dreamer_env 
    |  |
    │  ├─job_service
    |  |  └─.job_env 
    |  |
    │  ├─mentor_service
    |  |  └─.mentor_env 
    |  |
    │  ├─notification_service
    |  |  └─.notification_env 
    |  |
    │  ├─organization_service
    |  |  └─.organization_env 
    |  |
    │  ├─textbook_service
    |  |  └─.textbook_env 
    |  |
    │  └─user_service
    |     └─.user_env    
    |
    └─shared    
    ```

3. ### 共通イメージのビルド

    ```cmd
    docker build -t karynos/be-python-base:latest -f ./docker/python-base.Dockerfile .
    ```

## 開発環境の起動方法

```cmd
docker compose -f ./docker/dev/docker-compose.yml up --build
```
## 共通イメージの内容

```
FROM python:3.12-slim

WORKDIR /app

COPY ../shared/requirements.txt /tmp/shared-requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/shared-requirements.txt
```

