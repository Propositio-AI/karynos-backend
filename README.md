# karynos-backend

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link)

## 環境構築方法

下記は初回のみ行ってください

1. ### Gitからダウンロード

    ```cmd
    git clone https://github.com/Propositio-AI/karynos-backend.git
    cd karynos-backend
    ```

2. ### .envファイルのダウンロード

    `.env`は[Googleドライブ](https://drive.google.com/drive/folders/12U9-36mWvZU0-SYGxlg3OeA4gWnsi3La?usp=drive_link)にあります。適切な場所に配置してください。

3. ### 共通イメージのビルド

    ```cmd
    docker build -t karynos/be-python-base:latest -f ./docker/python-base.Dockerfile .
    ```

## dockerの起動

```cmd
docker compose -f ./docker/dev/docker-compose.yml up --build
```