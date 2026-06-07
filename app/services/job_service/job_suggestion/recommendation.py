from datetime import datetime
import os
from typing import Any

import chromadb
from chromadb.utils import embedding_functions


class RuleBasedProfileGenerator:
    @staticmethod
    def generate_profile(init_answers: list[dict[str, Any]], recent_jobs: list[dict[str, Any]]) -> str:
        answer_texts = [x.get("option_text", "") for x in init_answers if x.get("option_text")]
        liked = [x for x in recent_jobs if x.get("good")]
        disliked = [x for x in recent_jobs if x.get("bad")]

        parts = []
        if answer_texts:
            parts.append("初期診断の傾向: " + " / ".join(answer_texts[:5]))
        if liked:
            parts.append("好む職業: " + ", ".join([x.get("name", "") for x in liked[:3]]))
        if disliked:
            parts.append("避けたい職業: " + ", ".join([x.get("name", "") for x in disliked[:3]]))

        profile = "。".join([x for x in parts if x]).strip()
        if not profile:
            profile = "仕事選択で適性・興味・将来性を重視するユーザー。"
        return profile


class VectorSearchRecommender:
    def __init__(self, persist_directory: str | None = None):
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./ChromaDB")
        self.collection_name = os.getenv("CHROMA_JOB_COLLECTION", "job_vector_db")
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        try:
            embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self.client = None
            self.collection = None

    def rebuild_collection(self) -> bool:
        if not self.client:
            return False

        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            # Collection may not exist yet; this is safe to ignore.
            pass

        self._init_db()
        return self.collection is not None

    @staticmethod
    def job_to_document(job: Any) -> str:
        return "\n".join(
            [
                f"職業名: {getattr(job, 'name', '')}",
                f"仕事内容: {getattr(job, 'description', '')}",
                f"特性: {getattr(job, 'personality_traits', '')}",
                f"魅力: {getattr(job, 'appeal_points', '')}",
                f"成長: {getattr(job, 'growth_opportunities', '')}",
            ]
        )

    def sync_jobs(self, jobs: list[Any], rebuild: bool = False) -> int:
        if not self.collection:
            return 0

        if rebuild and not self.rebuild_collection():
            return 0

        ids = []
        documents = []
        metadatas = []

        for job in jobs:
            job_id = getattr(job, "job_id", None)
            if job_id is None:
                continue
            ids.append(str(job_id))
            documents.append(self.job_to_document(job))
            metadatas.append(
                {
                    "job_name": getattr(job, "name", "") or "",
                    "salary": int(getattr(job, "salary", 0) or 0),
                    "age": int(getattr(job, "age", 0) or 0),
                    "description": getattr(job, "description", "") or "",
                    "updated_at": datetime.now().isoformat(),
                }
            )

        if not ids:
            return 0

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(ids)

    def search_jobs(self, profile: str, top_k: int = 10):
        if not self.collection:
            return []

        results = self.collection.query(query_texts=[profile], n_results=max(1, top_k))
        ids = (results.get("ids") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]

        recommendations = []
        for index, (job_id, distance, metadata) in enumerate(zip(ids, distances, metadatas), start=1):
            score = round((1 - float(distance)) * 100, 1)
            recommendations.append(
                {
                    "job_id": int(job_id) if str(job_id).isdigit() else job_id,
                    "job_name": (metadata or {}).get("job_name", ""),
                    "score": score,
                    "reason": "プロファイルとのベクトル類似度が高い",
                    "rank": index,
                }
            )
        return recommendations


class RecommendationProcessor:
    def __init__(self, recommender: VectorSearchRecommender):
        self.recommender = recommender

    def generate_recommendations(self, profile: str, recent_jobs: list[dict[str, Any]], top_k: int = 10):
        viewed_ids = {int(x.get("job_id", 0)) for x in recent_jobs if x.get("job_id")}
        raw = self.recommender.search_jobs(profile=profile, top_k=top_k * 3)

        output = []
        for row in raw:
            job_id = int(row.get("job_id", 0) or 0)
            if job_id in viewed_ids:
                continue
            output.append(row)
            if len(output) >= top_k:
                break

        if not output:
            output = raw[:top_k]
        return output
