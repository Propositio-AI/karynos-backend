import os
from datetime import datetime
from typing import Any

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# text-embedding-3-small のデフォルト出力次元
# 変更する場合は Qdrant コレクションを再構築すること (make qdrant-clean && make sync-vectordb-rebuild)
_VECTOR_DIM = 1536
_EMBED_BATCH = 100  # OpenAI API に一度に投げる最大テキスト数


class RuleBasedProfileGenerator:
    @staticmethod
    def generate_profile(
        init_answers: list[dict[str, Any]], recent_jobs: list[dict[str, Any]]
    ) -> str:
        answer_texts = [
            x.get("option_text", "") for x in init_answers if x.get("option_text")
        ]
        liked = [x for x in recent_jobs if x.get("good")]
        disliked = [x for x in recent_jobs if x.get("bad")]

        parts = []
        if answer_texts:
            parts.append("初期診断の傾向: " + " / ".join(answer_texts[:5]))
        if liked:
            parts.append(
                "好む職業: " + ", ".join([x.get("name", "") for x in liked[:3]])
            )
        if disliked:
            parts.append(
                "避けたい職業: " + ", ".join([x.get("name", "") for x in disliked[:3]])
            )

        profile = "。".join([x for x in parts if x]).strip()
        if not profile:
            profile = "仕事選択で適性・興味・将来性を重視するユーザー。"
        return profile


class VectorSearchRecommender:
    def __init__(self, host: str | None = None, port: int | None = None):
        self.host = host or os.getenv("QDRANT_HOST", "qdrant")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_JOB_COLLECTION", "job_vector_db")
        self._embedding_model = os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self._openai: OpenAI | None = None
        self.client: QdrantClient | None = None
        self._init_client()

    # ── 初期化 ───────────────────────────────────────────────────────────

    def _init_client(self) -> None:
        try:
            self.client = QdrantClient(host=self.host, port=self.port, timeout=5)
            existing = {c.name for c in self.client.get_collections().collections}
            if self.collection_name not in existing:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=_VECTOR_DIM, distance=Distance.COSINE
                    ),
                )
        except Exception:
            self.client = None

    def is_ready(self) -> bool:
        return self.client is not None

    # ── OpenAI クライアント (遅延初期化) ────────────────────────────────

    def _get_openai(self) -> OpenAI:
        if self._openai is None:
            self._openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._openai

    def _encode(self, text: str) -> list[float]:
        """テキスト 1 件をベクトル化する。"""
        resp = self._get_openai().embeddings.create(
            model=self._embedding_model,
            input=text,
        )
        return resp.data[0].embedding

    def _encode_batch(self, texts: list[str]) -> list[list[float]]:
        """テキスト複数件を一括ベクトル化する（API コール削減）。"""
        resp = self._get_openai().embeddings.create(
            model=self._embedding_model,
            input=texts,
        )
        # index 順に並べ直して返す
        return [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]

    # ── ドキュメント生成 ─────────────────────────────────────────────────

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

    # ── 同期 ─────────────────────────────────────────────────────────────

    def rebuild_collection(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=_VECTOR_DIM, distance=Distance.COSINE),
            )
            return True
        except Exception:
            return False

    def sync_jobs(self, jobs: list[Any], rebuild: bool = False) -> int:
        if not self.client:
            return 0
        if rebuild and not self.rebuild_collection():
            return 0

        # job_id と document テキストを収集
        job_ids: list[int] = []
        docs: list[str] = []
        payloads: list[dict] = []

        for job in jobs:
            job_id = getattr(job, "job_id", None)
            if job_id is None:
                continue
            job_ids.append(int(job_id))
            docs.append(self.job_to_document(job))
            payloads.append(
                {
                    "job_name": getattr(job, "name", "") or "",
                    "salary": int(getattr(job, "salary", 0) or 0),
                    "age": int(getattr(job, "age", 0) or 0),
                    "description": getattr(job, "description", "") or "",
                    "updated_at": datetime.now().isoformat(),
                }
            )

        if not job_ids:
            return 0

        # OpenAI API バッチエンコード → Qdrant upsert
        for i in range(0, len(job_ids), _EMBED_BATCH):
            batch_ids = job_ids[i : i + _EMBED_BATCH]
            batch_docs = docs[i : i + _EMBED_BATCH]
            batch_payloads = payloads[i : i + _EMBED_BATCH]

            vectors = self._encode_batch(batch_docs)
            points = [
                PointStruct(id=jid, vector=vec, payload=pl)
                for jid, vec, pl in zip(batch_ids, vectors, batch_payloads)
            ]
            self.client.upsert(collection_name=self.collection_name, points=points)

        return len(job_ids)

    # ── 検索 ─────────────────────────────────────────────────────────────

    def search_jobs(self, profile: str, top_k: int = 10) -> list[dict[str, Any]]:
        if not self.client:
            return []

        result = self.client.query_points(
            collection_name=self.collection_name,
            query=self._encode(profile),
            limit=top_k,
        )
        return [
            {
                "job_id": hit.id,
                "job_name": (hit.payload or {}).get("job_name", ""),
                "score": round(hit.score * 100, 1),
                "reason": "プロファイルとのベクトル類似度が高い",
                "rank": i + 1,
            }
            for i, hit in enumerate(result.points)
        ]

    def search_by_text(self, text: str, top_k: int = 20) -> list[dict[str, Any]]:
        """任意テキストクエリで類似ジョブを検索する（フリー検索用）。"""
        return self.search_jobs(text, top_k=top_k)


class RecommendationProcessor:
    def __init__(self, recommender: VectorSearchRecommender):
        self.recommender = recommender

    def generate_recommendations(
        self, profile: str, recent_jobs: list[dict[str, Any]], top_k: int = 10
    ):
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
