from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from uuid import UUID
from datetime import datetime
import os

from crud import history_crud, jobs_crud
from schema import RecommendResponse, JobDetailResponse, ViewingHistoryResponse, ViewingHistoryItem, JobSearchResponse, JobSearchResult
from job_suggestion import (
    DataAggregator,
    JobSuggestionAnalyzer,
    VectorSearchRecommender,
    RecommendationProcessor,
    JobSuggestionResponse,
    SuggestionDebugResponse,
    SuggestionProfileResponse,
    UserDataSummary,
    RuleBasedProfileGenerator,
    TopRecommendedJobMatch,
)
from shared.lib.auth import get_current_user_id
from job_suggestion.data_fetcher import JobHistoryDataFetcher

# /api/v1/job
router = APIRouter()

@router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def _(job_id: int):
    """job情報の取得"""
    response = jobs_crud.read([
        ["job_id", "==", job_id]
    ])
    if not response["success"] or not response["data"]:
        return status.HTTP_404_NOT_FOUND

    job = response["data"][0]

    payload = {
        "job_id": getattr(job, "job_id", 0),
        "name": getattr(job, "name", "") or "",
        "description": getattr(job, "description", "") or "",
        "imgs": getattr(job, "imgs", []) or [],
        "salary": int(getattr(job, "salary", 0) or 0),
        "level": int(getattr(job, "level", 0) or 0),
        "end_time": getattr(job, "end_time", "") or "",
        "holiday": int(getattr(job, "holiday", 0) or 0),
        "overtime_hours": int(getattr(job, "overtime_hours", 0) or 0),
        "age": int(getattr(job, "age", 0) or 0),
        "tenure_years": int(getattr(job, "tenure_years", 0) or 0),
        "marriage_age": int(getattr(job, "marriage_age", 0) or 0),
        "gender_ratio": float(getattr(job, "gender_ratio", 0.0) or 0.0),
        "romance_rate": float(getattr(job, "romance_rate", 0.0) or 0.0),
        "social_signification": getattr(job, "social_signification", "") or "",
        "personality_traits": getattr(job, "personality_traits", "") or "",
        "growth_opportunities": getattr(job, "growth_opportunities", "") or "",
        "wrong_image": getattr(job, "wrong_image", "") or "",
        "uniform": bool(getattr(job, "uniform", False) or False),
        "work_life_balance": float(getattr(job, "work_life_balance", 0.0) or 0.0),
        "future_outlook": getattr(job, "future_outlook", "") or "",
        "rarity": float(getattr(job, "rarity", 0.0) or 0.0),
        "scandal_history": getattr(job, "scandal_history", "") or "",
        "focus_on_education": bool(getattr(job, "focus_on_education", False) or False),
        "focus_on_achievements": bool(getattr(job, "focus_on_achievements", False) or False),
        "appeal_points": getattr(job, "appeal_points", "") or "",
        "daily_routine": getattr(job, "daily_routine", "") or "",
        "comments": getattr(job, "comments", "") or "",
        "skills": getattr(job, "skills", []) or [],
        "certifications": getattr(job, "certifications", []) or [],
        "companies": getattr(job, "companies", []) or [],
        "talents": getattr(job, "talents", []) or [],
        "interests": getattr(job, "interests", []) or [],
    }

    return JobDetailResponse.model_validate(payload)

@router.get("/history", response_model=ViewingHistoryResponse)
async def get_viewing_history(
    dreamer_id: UUID = Depends(get_current_user_id),
    limit: int = 50,
    offset: int = 0
):
    """
    ユーザーの閲覧履歴を取得
    
    Args:
        dreamer_id: 認証から取得したユーザーID（Depends）
        limit: 取得する件数（デフォルト: 50）
        offset: オフセット（デフォルト: 0）
    
    Returns:
        閲覧履歴一覧（新しい順）
    """
    try:
        # ユーザーの閲覧履歴を取得（新しい順）
        response = history_crud.read([
            ["dreamer_id", "==", dreamer_id]
        ])
        
        if not response["success"]:
            raise HTTPException(
                status_code=500,
                detail="閲覧履歴の取得に失敗しました"
            )
        
        histories = response["data"] or []
        
        # created_atで降順にソート（新しい順）
        histories = sorted(
            histories,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True
        )
        
        # オフセットとリミットを適用
        total_count = len(histories)
        paginated_histories = histories[offset:offset + limit]
        
        # 各履歴アイテムを組み立て
        items = []
        for history in paginated_histories:
            try:
                # 対応するジョブ情報を取得
                job_response = jobs_crud.read([
                    ["job_id", "==", getattr(history, "job_id", None)]
                ])
                
                job = None
                if job_response["success"] and job_response["data"]:
                    job = job_response["data"][0]
                
                # 履歴アイテムを作成
                item = ViewingHistoryItem(
                    history_id=getattr(history, "history_id"),
                    job_id=getattr(history, "job_id"),
                    job_name=getattr(job, "name", "") if job else "",
                    job_imgs=getattr(job, "imgs", []) if job else [],
                    good=getattr(history, "good", False),
                    bad=getattr(history, "bad", False),
                    save=getattr(history, "save", False),
                    created_at=getattr(history, "created_at", datetime.now()).isoformat()
                )
                items.append(item)
            except Exception as e:
                print(f"[Error] 履歴アイテム処理エラー (history_id={getattr(history, 'history_id')}): {e}")
                continue
        
        # レスポンスを構成
        response_model = ViewingHistoryResponse(
            total_count=total_count,
            items=items,
            created_at=datetime.now().isoformat()
        )
        
        return response_model
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] 閲覧履歴取得エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"閲覧履歴取得中にエラーが発生しました: {str(e)}"
        )

@router.get("/search", response_model=JobSearchResponse)
async def search_jobs(q: str, limit: int = 20, offset: int = 0):
    """
    職業を自由度高く検索
    
    - 職業名から検索
    - 得意なことから検索
    - 性格特性から検索
    - アピールポイントから検索
    - 説明から検索
    など、様々な属性から検索可能
    
    ベクトル類似度検索を使用して、クエリの意図を理解した検索結果を返します。
    
    Args:
        q: 検索クエリ（日本語対応）
        limit: 取得する件数（デフォルト: 20）
        offset: オフセット（デフォルト: 0）
    
    Returns:
        検索結果の職業リスト（類似度スコア順）
    
    Example:
        /search?q=人と関わる仕事&limit=10
        /search?q=創造性が必要&limit=15
        /search?q=安定して稼げる&limit=20
        /search?q=プログラマー&limit=10
    """
    try:
        # バリデーション
        if not q or not q.strip():
            raise HTTPException(
                status_code=400,
                detail="検索クエリが空です"
            )
        
        if limit < 1 or limit > 100:
            limit = 20
        if offset < 0:
            offset = 0
        
        # Chroma DBでベクトル検索を実行
        recommender = VectorSearchRecommender()
        
        if not recommender.collection:
            raise HTTPException(
                status_code=500,
                detail="ベクトルDB（Chroma）が初期化されていません。管理者に連絡してください。"
            )
        
        # クエリの言語を検出して最適化
        search_query = q.strip()
        
        # ベクトル検索実行
        results = recommender.collection.query(
            query_texts=[search_query],
            n_results=limit + offset  # offset対応
        )
        
        if not results or not results["ids"] or not results["ids"][0]:
            # マッチなし - 空結果を返す
            return JobSearchResponse(
                query=q,
                total_count=0,
                items=[],
                created_at=datetime.now().isoformat()
            )
        
        # 結果を抽出
        job_ids = results["ids"][0]
        distances = results["distances"][0]
        
        # offsetを適用したアイテムを処理
        items = []
        for job_id_str, distance in list(zip(job_ids, distances))[offset:offset + limit]:
            try:
                job_id = int(job_id_str) if isinstance(job_id_str, str) and job_id_str.isdigit() else job_id_str
                
                # ジョブ詳細を取得
                job_response = jobs_crud.read([
                    ["job_id", "==", job_id]
                ])
                
                if not job_response["success"] or not job_response["data"]:
                    continue
                
                job = job_response["data"][0]
                
                # コサイン距離をスコアに変換
                similarity_score = (1 - distance) * 100
                
                # 検索結果アイテムを作成
                item = JobSearchResult(
                    job_id=getattr(job, "job_id"),
                    name=getattr(job, "name", "") or "",
                    description=getattr(job, "description", "") or "",
                    imgs=getattr(job, "imgs", []) or [],
                    personality_traits=getattr(job, "personality_traits", "") or "",
                    appeal_points=getattr(job, "appeal_points", "") or "",
                    growth_opportunities=getattr(job, "growth_opportunities", "") or "",
                    similarity_score=round(similarity_score, 1)
                )
                items.append(item)
            except Exception as e:
                print(f"[Error] 検索結果処理エラー (job_id={job_id_str}): {e}")
                continue
        
        # レスポンスを構成
        response_model = JobSearchResponse(
            query=q,
            total_count=len(job_ids),
            items=items,
            created_at=datetime.now().isoformat()
        )
        
        return response_model
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] 職業検索エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"職業検索中にエラーが発生しました: {str(e)}"
        )

@router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「いいね」登録（履歴の更新）"""
    response = history_crud.update(
        [["history_id", "==", history_id]],
        {"good": True}
    )

    if not response["success"]:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

    return status.HTTP_200_OK

@router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「バッド」登録（履歴の更新）"""
    response = history_crud.update(
        [["history_id", "==", history_id]],
        {"bad": True}
    )
    if not response["success"]:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_200_OK

@router.put("/save/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「保存」登録（履歴の更新）"""
    response = history_crud.update(
        [["history_id", "==", history_id]],
        {"save": True}
    )
    if not response["success"]:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"message": "保存登録が完了しました"}

@router.get("/recommend", response_model=JobSuggestionResponse)
async def recommend_jobs(dreamer_id: UUID = Depends(get_current_user_id)):
    """
    Dreamerにおすすめの職業を推奨
    
    フロー:
    1. dreamer_serviceから初期質問回答を取得
    2. job_serviceのhistoryテーブルから職業評価を取得
    3. OpenAIでユーザープロファイルを生成
    4. Chroma DBでベクトル検索し、推奨職業を取得
    5. 過去の評価状況を付加して返す
    
    Args:
        dreamer_id: 認証から取得したユーザーID（Depends）
    
    Returns:
        推奨職業リスト（適合度スコア順）
    """
    try:
        # ===== Step 1: ユーザーデータを集約 =====
        print(f"\n[Job Suggestion] {dreamer_id} の推奨開始...")
        
        data_aggregator = DataAggregator()
        user_data = data_aggregator.aggregate_user_data(dreamer_id)
        
        if not user_data:
            raise HTTPException(
                status_code=400,
                detail="ユーザーデータの取得に失敗しました"
            )
        
        init_answers = user_data.get("init_answers", [])
        job_history = user_data.get("job_history", {})
        
        # 回答がない場合は分析不可
        if not init_answers and not job_history.get("good_jobs", []):
            raise HTTPException(
                status_code=400,
                detail="分析に必要なデータが不足しています（初期質問回答または職業評価が必要）"
            )
        
        print(f"  ✓ ユーザーデータ集約完了")
        print(f"    - 初期質問回答: {len(init_answers)}件")
        print(f"    - Good職業: {len(job_history.get('good_jobs', []))}件")
        print(f"    - Bad職業: {len(job_history.get('bad_jobs', []))}件")
        
        # ===== Step 2: ルールベースのプロファイルを生成 =====
        print(f"  [進捗] ルールベースのプロファイルを生成中...")
        
        # 直近10件の閲覧職業データを取得
        recent_jobs = JobHistoryDataFetcher.get_recent_viewed_jobs(dreamer_id, limit=10)

        print(recent_jobs, flush=True)  # 直近の閲覧職業データをログに出力
        
        # ルールベースでプロファイルを生成
        profile = RuleBasedProfileGenerator.generate_profile(init_answers, recent_jobs)
        
        print(f"  ✓ プロファイル生成完了（{len(profile)}文字）")
        print(profile, flush=True)  # 生成されたプロファイルをログに出力
        
        # ===== Step 3: ベクトル検索で推奨職業を取得 =====
        print(f"  [進捗] ベクトル検索実行中...")
        
        recommender = VectorSearchRecommender()
        processor = RecommendationProcessor(recommender)
        
        recommendation_result = processor.generate_recommendations(
            dreamer_id=dreamer_id,
            profile=profile,
            recent_jobs=recent_jobs,
            top_k=10
        )
        
        recommendation_data = None
        
        if not recommendation_result:
            print(f"  ⚠ 推奨職業がありません（DBが空の可能性）")
        else:
            recommendation_data = recommendation_result.get("top_recommendation_data")
        
        print(f"  ✓ 推奨職業取得完了")
        
        # ===== Step 4: レスポンスを構成 =====
        # recommendation_dataが辞書の場合、モデルに変換
        recommendation_model = None
        if recommendation_data:
            try:
                recommendation_model = TopRecommendedJobMatch(**recommendation_data)
            except Exception as e:
                print(f"[Error] レコメンデーションモデル変換エラー: {e}")
                recommendation_model = None
        
        response = JobSuggestionResponse(
            recommendation=recommendation_model,
            analysis_completed_at=datetime.now().isoformat()
        )
        
        print(f"  ✓ 推奨完了")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] 推奨処理エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"推奨処理中にエラーが発生しました: {str(e)}"
        )


@router.get("/recommend/debug", response_model=SuggestionDebugResponse)
async def recommend_jobs_debug(dreamer_id: UUID = Depends(get_current_user_id)):
    """
    【デバッグ用】推奨職業の生成プロセスを詳細に返す
    
    Args:
        dreamer_id: 認証から取得したユーザーID（Depends）
    
    Returns:
        ユーザーデータ概要、プロファイル、推奨職業の詳細
    """
    try:
        print(f"\n[Job Suggestion Debug] {dreamer_id} の推奨開始...")
        
        # ===== ユーザーデータを集約 =====
        data_aggregator = DataAggregator()
        user_data = data_aggregator.aggregate_user_data(dreamer_id)
        
        if not user_data:
            raise HTTPException(status_code=400, detail="ユーザーデータの取得に失敗しました")
        
        init_answers = user_data.get("init_answers", [])
        job_history = user_data.get("job_history", {})
        
        # ユーザーデータサマリーを作成
        user_data_summary = UserDataSummary(
            dreamer_id=dreamer_id,
            init_answers_count=len(init_answers),
            good_jobs_count=len(job_history.get("good_jobs", [])),
            bad_jobs_count=len(job_history.get("bad_jobs", [])),
            saved_jobs_count=len(job_history.get("saved_jobs", [])),
            total_jobs_viewed=job_history.get("total_jobs_viewed", 0)
        )
        
        print(f"  ✓ ユーザーデータサマリー作成完了")
        
        # ===== 直近10件の閲覧職業データを取得 =====
        recent_jobs = JobHistoryDataFetcher.get_recent_viewed_jobs(dreamer_id, limit=10)
        
        # ===== プロファイルを生成 =====
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI APIキーが設定されていません")
        
        analyzer = JobSuggestionAnalyzer(api_key=api_key)
        profile = analyzer.analyze_user_profile(user_data)
        
        if not profile:
            raise HTTPException(status_code=500, detail="プロファイルの生成に失敗しました")
        
        profile_response = SuggestionProfileResponse(
            profile_text=profile,
            generated_at=datetime.now().isoformat()
        )
        
        print(f"  ✓ プロファイル生成完了")
        
        # ===== 推奨職業を取得 =====
        recommender = VectorSearchRecommender()
        processor = RecommendationProcessor(recommender)
        
        recommendations = processor.generate_recommendations(
            dreamer_id=dreamer_id,
            profile=profile,
            recent_jobs=recent_jobs,
            top_k=10
        )
        
        if not recommendations:
            recommendations = []
        
        print(f"  ✓ 推奨職業取得完了")
        
        # ===== デバッグレスポンスを構成 =====
        response = SuggestionDebugResponse(
            dreamer_id=dreamer_id,
            user_data_summary=user_data_summary,
            profile=profile_response,
            recommendations=recommendations
        )
        
        print(f"  ✓ デバッグ推奨完了")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] デバッグ推奨エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/sync-chromadb", status_code=status.HTTP_200_OK)
async def sync_jobs_to_chromadb():
    """
    【管理者用】PostgreSQLのjobsテーブルデータをChroma DBに同期
    
    全ての職業データを取得し、Chroma DBのベクトルDBに登録します。
    既存のデータは削除され、最新のデータで上書きされます。
    
    Returns:
        同期結果の統計情報
    """
    try:
        print(f"\n[Chroma DB Sync] 職業データの同期を開始...")
        
        # ===== Step 1: PostgreSQLから全職業データを取得 =====
        response = jobs_crud.read([])  # フィルタなしで全件取得
        
        if not response["success"]:
            raise HTTPException(
                status_code=500,
                detail="職業データの取得に失敗しました"
            )
        
        jobs = response["data"] or []
        
        if not jobs:
            raise HTTPException(
                status_code=404,
                detail="職業データが見つかりません"
            )
        
        print(f"  ✓ PostgreSQLから{len(jobs)}件の職業データを取得")
        
        # ===== Step 2: Chroma DBを初期化 =====
        recommender = VectorSearchRecommender()
        
        if not recommender.collection:
            raise HTTPException(
                status_code=500,
                detail="Chroma DBの初期化に失敗しました"
            )
        
        # 既存のコレクションをクリア
        try:
            # 全データを削除
            existing_ids = recommender.collection.get()["ids"]
            if existing_ids:
                recommender.collection.delete(ids=existing_ids)
                print(f"  ✓ 既存データ{len(existing_ids)}件を削除")
        except Exception as e:
            print(f"  [Warning] 既存データの削除に失敗: {e}")
        
        # ===== Step 3: 各職業データをChroma DBに登録 =====
        success_count = 0
        failed_count = 0
        
        documents = []
        metadatas = []
        ids = []
        
        for job in jobs:
            try:
                # 職業の特徴を結合したテキストを作成
                # Chroma DBではこのテキストがベクトル化される
                job_text_parts = [
                    f"職業名: {job.name}",
                    f"説明: {getattr(job, 'description', '') or ''}",
                    f"性格特性: {getattr(job, 'personality_traits', '') or ''}",
                    f"成長機会: {getattr(job, 'growth_opportunities', '') or ''}",
                    f"アピールポイント: {getattr(job, 'appeal_points', '') or ''}",
                ]
                
                job_text = "\n".join([part for part in job_text_parts if part])
                
                # メタデータを作成
                metadata = {
                    "job_name": job.name,
                    "description": getattr(job, "description", "") or "",
                    "personality_traits": getattr(job, "personality_traits", "") or "",
                    "growth_opportunities": getattr(job, "growth_opportunities", "") or "",
                    "appeal_points": getattr(job, "appeal_points", "") or "",
                }
                
                documents.append(job_text)
                metadatas.append(metadata)
                ids.append(str(job.job_id))
                
            except Exception as e:
                print(f"  [Error] job_id={job.job_id} の処理に失敗: {e}")
                failed_count += 1
        
        # バッチで登録
        if documents:
            try:
                recommender.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                success_count = len(documents)
                print(f"  ✓ {success_count}件の職業データをChroma DBに登録完了")
            except Exception as e:
                print(f"  [Error] Chroma DBへの登録に失敗: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Chroma DBへの登録に失敗しました: {str(e)}"
                )
        
        # ===== Step 4: 結果を返す =====
        result = {
            "success": True,
            "message": [f"Chroma DBへの同期が完了しました"],
            "data": {
                "total_jobs": len(jobs),
                "success_count": success_count,
                "failed_count": failed_count,
                "synced_at": datetime.now().isoformat()
            }
        }
        
        print(f"  ✓ 同期完了（成功: {success_count}, 失敗: {failed_count}）")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Error] Chroma DB同期エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"同期処理中にエラーが発生しました: {str(e)}"
        )