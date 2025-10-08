# textbook_service

## フォルダ構成

```

C:.
│   Dockerfile
│   README.md
│   requirements.txt
│
├───app
│   │   main.py              # gRPCサーバー起動コード
│   │   service.py           # モデル呼び出し
│   │
│   ├───prompts              # プロンプト
│   │       prompt.txt
│   │
│   └───proto
└───tests
        test.py

```