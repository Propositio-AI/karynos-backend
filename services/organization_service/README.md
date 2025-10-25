# Organization Service

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link#2919a9038f38809db197c837837c5488)

| **項目** | **内容** |
|-----------|-----------|
| **サービス名** | organization_service |
| **主な責務** | ・組織ID・組織情報の管理 |
| **通信方法** | API |
| **ルート** | `organization/` |
| **構成コンテナ** | APIサーバー（organization_service）<br>DBサーバー（organization-db） |
| **実装言語** | Python |

## フォルダ構成

```
│  .mentor_env                                   // 環境変数
│  Dockerfile                                
│  README.md
│  requirements.txt                           // Pythonライブラリ一覧 
│
├─app
│  │  crud.py                                 // DB操作関係
│  │  main.py                                 // 実行不ファイル
│  │　schemas.py                              // 型定義ファイル
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