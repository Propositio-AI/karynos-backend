"""
Data Fetcher Module

責務:
- dreamer_serviceから初期質問の回答を取得
- job_serviceのhistoryテーブルから職業評価データを取得
- 外部サービスからのデータ取得を一元管理
"""

from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

from crud import history_crud, jobs_crud
from shared.lib.API import Client


class DreamerServiceClient:
    """dreamer_serviceとの通信を管理"""
    
    BASE_URL = "http://dreamer-service:8000/api/v1"
    
    @classmethod
    def get_init_answers_history(cls, dreamer_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """
        ユーザーの初期診断回答履歴を取得
        
        Args:
            dreamer_id: ユーザーID
        
        Returns:
            回答履歴データのリスト。取得に失敗した場合はNone
        
        Response形式:
            [
                {
                    "answer_id": "xxx",
                    "question_id": "xxx",
                    "question_text": "新しい複雑な機械を...",
                    "option_id": "xxx",
                    "option_text": "説明書を最初から...",
                    "question_version": 1,
                    "answered_at": "2026-02-22T10:00:00"
                },
                ...
            ]
        """
        try:
            url = f"{cls.BASE_URL}/init-answers/history"
            
            # shared/lib/API/Client を使用
            client = Client(key=str(dreamer_id))
            response = client.get(url)
            
            # レスポンス形式: {"success": bool, "message": list[str], "data": Any}
            if not isinstance(response, dict):
                print(f"[Error] dreamer_service予期しないレスポンス形式: {type(response)}")
                return None
            
            if not response.get("success", False):
                messages = response.get("message", ["不明なエラー"])
                print(f"[Error] dreamer_service取得失敗: {', '.join(messages)}")
                return None
            
            data = response.get("data")
            if data is None:
                print(f"[Warning] dreamer_serviceからデータが返されませんでした")
                return []
            
            if not isinstance(data, list):
                print(f"[Error] dreamer_service data形式エラー: 期待list, 実際{type(data)}")
                return None
            
            return data
        
        except Exception as e:
            print(f"[Error] dreamer_service通信失敗: {e}")
            return None


class JobHistoryDataFetcher:
    """job_serviceのhistoryテーブルからデータを取得"""
    
    @staticmethod
    def get_user_job_history(dreamer_id: UUID) -> Optional[Dict[str, Any]]:
        """
        ユーザーの職業評価履歴を取得
        
        Args:
            dreamer_id: ユーザーID
        
        Returns:
            職業評価データの集約結果：
            {
                "total_jobs_viewed": 10,
                "good_jobs": [
                    {
                        "job_id": 1,
                        "job_name": "営業職",
                        "good": True,
                        "bad": False,
                        "save": False
                    },
                    ...
                ],
                "bad_jobs": [
                    ...
                ],
                "saved_jobs": [
                    ...
                ]
            }
        """
        try:
            # ユーザーの全履歴を取得
            history_response = history_crud.read([
                ["dreamer_id", "==", str(dreamer_id)]
            ])

            print(dreamer_id, flush=True)
            
            if not history_response["success"]:
                print(f"[Error]履歴取得失敗: {history_response.get('message')}")
                return None
            
            history_data = history_response["data"] or []
            
            if not history_data:
                return {
                    "total_jobs_viewed": 0,
                    "good_jobs": [],
                    "bad_jobs": [],
                    "saved_jobs": []
                }
            
            # Good/Bad/Saved を分類
            good_jobs = []
            bad_jobs = []
            saved_jobs = []
            
            for record in history_data:
                job_id = record.job_id
                
                # 職業情報を取得
                job_response = jobs_crud.read([
                    ["job_id", "==", job_id]
                ])
                
                job_name = ""
                if job_response["success"] and job_response["data"]:
                    job_name = job_response["data"][0].name
                
                job_info = {
                    "history_id": str(record.history_id),
                    "job_id": job_id,
                    "job_name": job_name,
                    "good": record.good,
                    "bad": record.bad,
                    "save": record.save,
                    "created_at": record.created_at.isoformat() if record.created_at else ""
                }
                
                if record.good:
                    good_jobs.append(job_info)
                if record.bad:
                    bad_jobs.append(job_info)
                if record.save:
                    saved_jobs.append(job_info)
            
            return {
                "total_jobs_viewed": len(history_data),
                "good_jobs": good_jobs,
                "bad_jobs": bad_jobs,
                "saved_jobs": saved_jobs
            }
        
        except Exception as e:
            print(f"[Error] 履歴処理中にエラー: {e}")
            return None
    
    @staticmethod
    def get_job_details(job_id: int) -> Optional[Dict[str, Any]]:
        """
        職業の詳細情報を取得
        
        Args:
            job_id: 職業ID
        
        Returns:
            職業の詳細情報
        """
        try:
            job_response = jobs_crud.read([
                ["job_id", "==", job_id]
            ])
            
            if not job_response["success"] or not job_response["data"]:
                return None
            
            job = job_response["data"][0]
            return {
                "job_id": job.job_id,
                "name": job.name,
                "description": getattr(job, "description", ""),
                "personality_traits": getattr(job, "personality_traits", ""),
                "growth_opportunities": getattr(job, "growth_opportunities", ""),
                "appeal_points": getattr(job, "appeal_points", ""),
            }
        
        except Exception as e:
            print(f"[Error] 職業詳細取得失敗: {e}")
            return None
    
    @staticmethod
    def get_recent_viewed_jobs(dreamer_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        ユーザーが直近に閲覧した職業データを取得（全フィールド）
        
        Args:
            dreamer_id: ユーザーID
            limit: 取得件数（デフォルト: 10）
        
        Returns:
            直近に閲覧した職業の全詳細データリスト
        """
        try:
            # ユーザーの全履歴を取得
            history_response = history_crud.read([
                ["dreamer_id", "==", str(dreamer_id)]
            ])
            
            if not history_response["success"] or not history_response["data"]:
                return []
            
            history_data = history_response["data"] or []
            
            # 作成日時でソート（新しい順）
            history_data_sorted = sorted(
                history_data,
                key=lambda x: x.created_at if x.created_at else datetime.min,
                reverse=True
            )
            
            # 最新10件を取得
            recent_history = history_data_sorted[:limit]
            
            viewed_jobs = []
            for record in recent_history:
                job_id = record.job_id
                
                # 職業情報を取得
                job_response = jobs_crud.read([
                    ["job_id", "==", job_id]
                ])
                
                if not job_response["success"] or not job_response["data"]:
                    continue
                
                job = job_response["data"][0]
                
                # 職業の全データを取得
                job_info = {
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
                    # 閲覧履歴情報
                    "good": record.good,
                    "bad": record.bad,
                    "save": record.save,
                    "viewed_at": record.created_at.isoformat() if record.created_at else ""
                }
                
                viewed_jobs.append(job_info)
            
            return viewed_jobs
        
        except Exception as e:
            print(f"[Error] 直近閲覧職業取得エラー: {e}")
            return []


class DataAggregator:
    """dreamer_serviceとjob_serviceからのデータを統合"""
    
    @staticmethod
    def aggregate_user_data(dreamer_id: UUID) -> Optional[Dict[str, Any]]:
        """
        ユーザーの全関連データを集約
        
        Args:
            dreamer_id: ユーザーID
        
        Returns:
            統合されたユーザーデータ：
            {
                "dreamer_id": "xxx",
                "init_answers": [...],
                "job_history": {
                    "total_jobs_viewed": 10,
                    "good_jobs": [...],
                    "bad_jobs": [...],
                    "saved_jobs": [...]
                }
            }
            初期質問回答が取得できない場合はNone
        """
        try:
            # 初期質問回答と職業評価を取得
            init_answers = DreamerServiceClient.get_init_answers_history(dreamer_id)
            job_history = JobHistoryDataFetcher.get_user_job_history(dreamer_id)
            
            # 初期質問は必須
            if init_answers is None or len(init_answers) == 0:
                print("[Error] 初期質問回答が存在しません。診断を完了してください。")
                return None
            
            # 職業評価履歴はオプショナル（なくても動作する）
            if job_history is None:
                print("[Info] 職業評価履歴がありません。空のデータで続行します。")
                job_history = {
                    "total_jobs_viewed": 0,
                    "good_jobs": [],
                    "bad_jobs": [],
                    "saved_jobs": []
                }
            
            return {
                "dreamer_id": str(dreamer_id),
                "init_answers": init_answers,
                "job_history": job_history,
                "aggregated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"[Error] データ集約エラー: {e}")
            return None
