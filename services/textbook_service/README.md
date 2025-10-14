# Textbook Service

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link#2899a9038f38806c87c3eb958b177061)

| **項目** | **内容** |
|-----------|-----------|
| **サービス名** | textbook_service |
| **主な責務** | ・教科書の生成<br>・教科書の管理<br>・各教科書パーツの生成 |
| **通信方法** | API |
| **ルート** | `textbook/` |
| **構成コンテナ** | APIサーバー（textbook_service）<br>DBサーバー（textbook-db） |
| **実装言語** | Python |

## フォルダ構成

```
│  .textbook_env                                   // 環境変数
│  Dockerfile                                
│  README.md
│  requirements.txt                           // Pythonライブラリ一覧 
│
├─app
│  │  crud.py                                 // DB操作関係
│  │  main.py                                 // 実行不ファイル
│  │
│  ├─core                                      
│  │  │  config.py                            // 設定ファイル
│  │  │  db.py                                // DB接続関係
│  │
│  ├─models　　　　　　　　　　　　　　　　　　　 // DBテーブル関係
│  │ │   base.py                              
│  │
│  ├─route
│  │  │  main_router.py                       // ルートルーティング
│  │  │
│  │  ├─api
│  │  │  │  v1.py                             // APIルーティング
│  │  │
│  │  ├─ws
│  │     │  v1.py                             // WebSocketルーティング
│  │
│  └─shared
│
└─db
   │  init.sql                                 // DB初回実行ファイル
```

## テスト設計