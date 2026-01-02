import os
import chromadb
from chromadb.utils import embedding_functions


PERSIST_DIRECTORY = "./chroma_db"
LOCAL_EMBEDDING_MODEL = "sonoisa/sentence-bert-base-ja-mean-tokens"


def main():
    print("Connecting to Chroma DB...")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=LOCAL_EMBEDDING_MODEL
    )
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_or_create_collection(
        name="openai_precision_matching",
        embedding_function=ef,
    )

    # サンプル職業データ（必要に応じて置き換えてください）
    ids = ["job_1", "job_2", "job_3"]
    names = [
        "システムエンジニア",
        "製造ラインの組立工",
        "カスタマーサポート"
    ]
    analyses = [
        "ソフトウェア設計、コーディング、テストを行い、複雑なシステムの論理的構築が得意。",
        "手先が器用でルーチン作業の正確性が高い。機械や工具の扱いに長けている。",
        "対人コミュニケーションが得意で、顧客の問題をヒアリングして解決に導く能力がある。"
    ]

    documents = [
        f"{names[i]}: {analyses[i]}" for i in range(len(ids))
    ]

    metadatas = [
        {"name": names[i], "analysis": analyses[i]} for i in range(len(ids))
    ]

    # 既存のデータを上書きしたい場合は一度削除してから追加
    try:
        existing = collection.count()
        if existing > 0:
            print(f"Existing documents: {existing}. Clearing collection first...")
            collection.delete()  # 全件削除
    except Exception:
        pass

    print("Adding sample documents...")
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print("Seed complete. Current count:", collection.count())


if __name__ == "__main__":
    main()
