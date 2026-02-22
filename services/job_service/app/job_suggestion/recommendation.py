"""
Recommendation Engine Module

責務:
- ユーザープロファイルとChromaDB内の職業DBから、最適な推奨職業を取得
- スコア計算と順位付け
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import chromadb
from chromadb.utils import embedding_functions


class RuleBasedProfileGenerator:
    """ルールベースでユーザープロファイルを生成"""
    
    @staticmethod
    def generate_profile(init_answers: List[Dict[str, Any]], recent_jobs: List[Dict[str, Any]]) -> str:
        """
        初回質問結果と直近の閲覧職業データからプロファイルを生成
        
        Args:
            init_answers: 初回質問の回答データ
            recent_jobs: 直近10件の閲覧職業データ（全詳細フィールド含む）
        
        Returns:
            生成されたプロファイル文字列
        """
        try:
            # 初回質問から回答パターンを抽出
            answer_texts = []
            for answer in init_answers:
                option_text = answer.get("option_text", "")
                if option_text:
                    answer_texts.append(option_text)
            
            # 好きな職業（Good評価）と避けたい職業（Bad評価）の詳細情報を分析
            good_jobs = []
            bad_jobs = []
            
            for job in recent_jobs:
                if job.get("good"):
                    good_jobs.append(job)
                elif job.get("bad"):
                    bad_jobs.append(job)
            
            # プロファイル文を生成
            profile_parts = []
            
            # 1. 初回質問の回答パターンから推測
            if answer_texts:
                profile_parts.append(f"初期診断から、この人物は以下の特性を示しています：{', '.join(answer_texts[:5])}")
            
            # 2. 好きな職業の詳細データから推測
            if good_jobs:
                good_job_names = [job.get("name", "") for job in good_jobs[:3]]
                
                # パーソナリティ特性を抽出
                personality_traits = []
                for job in good_jobs[:3]:
                    trait = job.get("personality_traits", "")
                    if trait:
                        personality_traits.append(trait)
                
                profile_parts.append(f"特に{', '.join(good_job_names)}のような職業に関心があります。")
                
                if personality_traits:
                    profile_parts.append(f"この人物のパーソナリティ特性として、{', '.join(personality_traits[:2])}が重要です。")
                
                # 成長機会や職業の魅力
                growth_opps = [job.get("growth_opportunities", "") for job in good_jobs if job.get("growth_opportunities")]
                if growth_opps:
                    profile_parts.append(f"キャリアの成長機会として、{growth_opps[0]}を重視しています。")
                
                # アピールポイント
                appeal_points = [job.get("appeal_points", "") for job in good_jobs if job.get("appeal_points")]
                if appeal_points:
                    profile_parts.append(f"職業の魅力として、{appeal_points[0]}を価値観としています。")
                
                # 給与・年齢層の傾向
                avg_salary = int(sum(job.get("salary", 0) for job in good_jobs) / len(good_jobs)) if good_jobs else 0
                avg_age = int(sum(job.get("age", 0) for job in good_jobs) / len(good_jobs)) if good_jobs else 0
                if avg_salary > 0:
                    profile_parts.append(f"平均年収{avg_salary}万円前後、平均年齢{avg_age}歳程度の職業帯に関心があります。")
                
                # 必要なスキルを抽出
                all_skills = set()
                for job in good_jobs:
                    skills = job.get("skills", [])
                    if isinstance(skills, list):
                        for skill in skills:
                            if isinstance(skill, dict) and skill.get("is_required"):
                                all_skills.add(skill.get("name", ""))
                if all_skills:
                    profile_parts.append(f"必要なスキル：{', '.join(list(all_skills)[:5])}")
                
                # 必要な才能を抽出
                all_talents = set()
                for job in good_jobs:
                    talents = job.get("talents", [])
                    if isinstance(talents, list):
                        for talent in talents:
                            if isinstance(talent, dict) and talent.get("is_required"):
                                all_talents.add(talent.get("name", ""))
                if all_talents:
                    profile_parts.append(f"必要な才能：{', '.join(list(all_talents)[:5])}")
                
                # 興味分野を抽出
                all_interests = set()
                for job in good_jobs:
                    interests = job.get("interests", [])
                    if isinstance(interests, list):
                        for interest in interests:
                            if isinstance(interest, dict) and interest.get("is_required"):
                                all_interests.add(interest.get("name", ""))
                if all_interests:
                    profile_parts.append(f"重視する興味分野：{', '.join(list(all_interests)[:4])}")
                
                # 所属企業の傾向
                all_companies = []
                for job in good_jobs:
                    companies = job.get("companies", [])
                    if isinstance(companies, list):
                        for company in companies:
                            if isinstance(company, dict):
                                all_companies.append(company.get("name", ""))
                if all_companies:
                    profile_parts.append(f"関心のある企業：{', '.join(list(set(all_companies))[:3])}")
            
            # 3. 避けたい職業の詳細データから推測
            if bad_jobs:
                bad_job_names = [job.get("name", "") for job in bad_jobs[:2]]
                profile_parts.append(f"一方、{', '.join(bad_job_names)}のような職業は避けたいと考えています。")
                
                # 避けたい理由を詳細に分析
                wrong_images = [job.get("wrong_image", "") for job in bad_jobs if job.get("wrong_image")]
                if wrong_images:
                    profile_parts.append(f"特に、{wrong_images[0]}という誤ったイメージがあるかもしれません。")
            
            # 4. ワーク・ライフ・バランスや職場環境の傾向
            if recent_jobs:
                avg_work_life_balance = sum(job.get("work_life_balance", 0.0) for job in recent_jobs) / len(recent_jobs) if recent_jobs else 0
                if avg_work_life_balance > 0:
                    balance_level = "高い" if avg_work_life_balance >= 0.7 else "中程度" if avg_work_life_balance >= 0.4 else "低い"
                    profile_parts.append(f"閲覧職業から判断すると、ワーク・ライフ・バランスを{balance_level}職場を求めています。")
                
                # 残業時間の傾向
                avg_overtime = sum(job.get("overtime_hours", 0) for job in recent_jobs) / len(recent_jobs) if recent_jobs else 0
                if avg_overtime > 0:
                    profile_parts.append(f"月平均残業時間{avg_overtime:.0f}時間程度の職業環境を検討しています。")
            
            # 総合的なプロファイルを構築
            profile = " ".join(profile_parts)
            
            # 最低限のプロファイルがない場合
            if len(profile) < 50:
                profile = "この人物は論理的思考を得意とし、キャリア開発に関心を持っています。直近の閲覧データから、多様な職業分野に関心があり、自分に合った職業を探索中です。"
            
            return profile
        
        except Exception as e:
            print(f"[Error] ルールベースプロファイル生成エラー: {e}")
            import traceback
            traceback.print_exc()
            return "ルールベース生成失敗：デフォルトプロファイル"


class VectorSearchRecommender:
    """Chroma DBを使用したベクトル類似度検索"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Args:
            persist_directory: Chroma DBの永続化ディレクトリ
        """
        self.persist_directory = persist_directory
        self._init_db()
    
    def _init_db(self):
        """Chroma DBの初期化"""
        try:
            # 日本語対応の安定したembeddingモデル
            # paraphrase-multilingual-MiniLM-L12-v2: 多言語対応、軽量、安定
            embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="job_vector_db",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[Job Suggestion] Chroma DB initialized: {self.persist_directory}")
        except Exception as e:
            print(f"[Error] Chroma DB初期化エラー: {e}")
            self.client = None
            self.collection = None
    
    def search_jobs(
        self,
        profile: str,
        top_k: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        ユーザープロファイルに基づいて職業を検索
        
        Args:
            profile: AI生成されたユーザープロファイル
            top_k: 取得する推奨職業数（デフォルト: 10）
        
        Returns:
            推奨職業リスト：
            [
                {
                    "job_id": 1,
                    "job_name": "営業職",
                    "similarity_score": 87.3,
                    "job_analysis": "この仕事は...",
                    "rank": 1
                },
                ...
            ]
        """
        try:
            if not self.collection:
                print("[Error] Chroma DBが初期化されていません")
                return None
            
            # プロファイルに基づいて検索
            results = self.collection.query(
                query_texts=[profile],
                n_results=top_k
            )
            
            if not results or not results["ids"] or not results["ids"][0]:
                print("[Warning] 職業DBに該当データがありません")
                return None
            
            # 結果を整形
            recommendations = []
            for i, (job_id, distance, metadata) in enumerate(
                zip(
                    results["ids"][0],
                    results["distances"][0],
                    results["metadatas"][0]
                )
            ):
                # コサイン距離をスコア（0-100）に変換
                similarity_score = (1 - distance) * 100
                
                recommendation = {
                    "job_id": int(job_id) if isinstance(job_id, str) and job_id.isdigit() else job_id,
                    "job_name": metadata.get("job_name", "Unknown"),
                    "similarity_score": round(similarity_score, 1),
                    "job_analysis": metadata.get("analysis", ""),
                    "rank": i + 1
                }
                recommendations.append(recommendation)
            
            return recommendations
        
        except Exception as e:
            print(f"[Error] 職業検索エラー: {e}")
            return None


class RecommendationProcessor:
    """推奨職業の処理と履歴への登録"""
    
    def __init__(self, search_recommender: VectorSearchRecommender):
        """
        Args:
            search_recommender: VectorSearchRecommenderインスタンス
        """
        self.search_recommender = search_recommender
    
    def generate_recommendations(
        self,
        dreamer_id: UUID,
        profile: str,
        recent_jobs: List[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> Optional[dict]:
        """
        ユーザーに対する推奨職業を生成
        
        Args:
            dreamer_id: ユーザーID（フロントエンドでの履歴登録用）
            profile: AI生成されたプロファイル
            recent_jobs: 直近10件の閲覧職業データ（除外対象）
            top_k: 推奨職業数
        
        Returns:
            最高スコア職業のマッチングデータを含む辞書
            {
                "top_recommendation_data": {
                    "job_id": int,
                    "imgs": [...],
                    "name": str,
                    "salary": int,
                    "similarity_score": float,
                    "age": int,
                    "description": str,
                    "history_id": str or None
                }
            }
        """
        try:
            if recent_jobs is None:
                recent_jobs = []
            
            # ベクトル検索で推奨職業を取得（余裕を持って多めに取得）
            recommendations = self.search_recommender.search_jobs(
                profile=profile,
                top_k=top_k * 3  # 除外後に十分な件数を確保
            )
            
            if not recommendations:
                print("[Warning] 推奨職業がありません")
                return {
                    "top_recommendation_data": None
                }
            
            # 直近10件の職業IDを取得
            excluded_job_ids = set(job.get("job_id") for job in recent_jobs if job.get("job_id"))
            
            # 除外対象の職業を除去し、top_k件取得
            filtered_recommendations = [
                rec for rec in recommendations 
                if rec.get("job_id") not in excluded_job_ids
            ][:top_k]
            
            print(f"[Info] 除外ジョブID数: {len(excluded_job_ids)}, フィルタリング後: {len(filtered_recommendations)}件")
            
            # 最高スコアの職業のマッチングデータを取得
            top_recommendation_data = None
            if filtered_recommendations:
                top_rec = filtered_recommendations[0]
                job_id = top_rec["job_id"]
                similarity_score = top_rec["similarity_score"]
                
                # 必要なデータを取得
                job_data = self._fetch_full_job_details(job_id, dreamer_id)
                if job_data:
                    # 適合度スコアを追加
                    job_data["similarity_score"] = similarity_score
                    top_recommendation_data = job_data
            
            return {
                "top_recommendation_data": top_recommendation_data
            }
        
        except Exception as e:
            print(f"[Error] 推奨生成エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _fetch_full_job_details(self, job_id: int, dreamer_id: UUID) -> Optional[Dict[str, Any]]:
        """
        指定されたjob_idのマッチング画面に必要なデータを取得
        
        Args:
            job_id: 職業ID
            dreamer_id: ユーザーID（history_id取得用）
        
        Returns:
            職業のマッチング用データ（TopRecommendedJobMatch形式）
            {
                "job_id": 1,
                "imgs": [...],
                "name": "...",
                "salary": 5000000,
                "age": 35,
                "description": "...",
                "history_id": "xxx"  # 必須
            }
        """
        from crud import jobs_crud, history_crud
        from models.HistoryTable import HistoryTableSchema
        from shared.utils.security import gen_uuid7
        
        try:
            response = jobs_crud.read([
                ["job_id", "==", job_id]
            ])
            
            if not response["success"] or not response["data"]:
                print(f"[Warning] Job ID {job_id} の詳細データが見つかりません")
                return None
            
            job = response["data"][0]
            
            # 推奨結果として常に新しい履歴レコードを作成
            # （既存の履歴を再利用するのではなく、新しい推奨として扱う）
            history_id = None
            try:
                # HistoryTableSchemaを使用してPydanticモデルを作成
                history_data = HistoryTableSchema(
                    job_id=job_id,
                    dreamer_id=dreamer_id,
                    good=False,
                    bad=False,
                    save=False
                )
                
                create_response = history_crud.create(history_data)
                
                if create_response["success"] and create_response["data"]:
                    created_history = create_response["data"]
                    history_id = str(created_history.history_id)
                    print(f"[Info] 新しい履歴を作成しました: {history_id}")
                else:
                    error_msg = create_response.get("message", "不明なエラー")
                    print(f"[Warning] Job ID {job_id} の履歴作成に失敗: {error_msg}")
                    # フォールバック：新しいUUIDを生成
                    history_id = str(gen_uuid7())
            
            except Exception as create_error:
                print(f"[Error] 履歴作成中にエラー: {create_error}")
                import traceback
                traceback.print_exc()
                # 失敗時もUUIDをhistory_idとして使用
                history_id = str(gen_uuid7())
            
            payload = {
                "job_id": getattr(job, "job_id", 0),
                "imgs": getattr(job, "imgs", []) or [],
                "name": getattr(job, "name", "") or "",
                "salary": int(getattr(job, "salary", 0) or 0),
                "age": int(getattr(job, "age", 0) or 0),
                "description": getattr(job, "description", "") or "",
                "history_id": history_id,
            }
            
            return payload
        
        except Exception as e:
            print(f"[Error] Job詳細データ取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _enrich_recommendations(
        self,
        dreamer_id: UUID,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        推奨職業に対して、ユーザーの過去の評価状況を追加
        
        Args:
            dreamer_id: ユーザーID
            recommendations: 推奨職業リスト
        
        Returns:
            ユーザーの評価状況を含む推奨職業リスト
        """
        from crud import history_crud
        
        enriched = []
        for rec in recommendations:
            job_id = rec["job_id"]
            
            # ユーザーのこの職業に対する過去の評価を確認
            history_response = history_crud.read([
                ["dreamer_id", "==", str(dreamer_id)],
                ["job_id", "==", job_id]
            ])
            
            previously_viewed = False
            previous_good = False
            previous_bad = False
            previous_save = False
            history_id = None
            
            if history_response["success"] and history_response["data"]:
                history_record = history_response["data"][0]
                previously_viewed = True
                previous_good = history_record.good
                previous_bad = history_record.bad
                previous_save = history_record.save
                history_id = str(history_record.history_id)
            
            enriched_rec = {
                **rec,
                "previously_viewed": previously_viewed,
                "previous_good": previous_good,
                "previous_bad": previous_bad,
                "previous_save": previous_save,
                "history_id": history_id
            }
            
            enriched.append(enriched_rec)
        
        return enriched
