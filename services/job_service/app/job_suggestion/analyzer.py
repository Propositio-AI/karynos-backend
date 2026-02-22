"""
Analysis Engine Module

責務:
- ユーザーの初期質問回答と職業評価履歴からAIでプロファイルを生成
- OpenAIを使用した職業適性分析
"""

from typing import Dict, Any, Optional
from openai import OpenAI


class JobSuggestionAnalyzer:
    """OpenAIを使用した職業適性分析エンジン"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Args:
            api_key: OpenAI APIキー
            model: 使用するモデル名
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def analyze_user_profile(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        ユーザーの初期回答と職業評価履歴を分析し、職業プロファイルを生成
        
        Args:
            user_data: DataAggregatorから取得したユーザーデータ
            {
                "dreamer_id": "xxx",
                "init_answers": [...],
                "job_history": {...}
            }
        
        Returns:
            AI生成された職業プロファイル（400文字程度）
        
        プロファイルフォーマット例:
            この仕事は、[操作対象]を操作・扱い、[目的]を達成することに特化しています。
            具体的には、[業務内容]を行います。
            思考タイプとしては、[思考パターン]が必要とされ、
            環境としては、[環境要件]で、[対人距離感]を持って働くことが適しています。
        """
        try:
            # プロンプトを構築
            prompt = self._build_analysis_prompt(user_data)
            
            # OpenAIでプロファイルを生成
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは職業適性分析の専門家です。ユーザーの行動とメタデータから、理想的な職業プロファイルを生成します。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"[Error] OpenAI分析エラー: {e}")
            return None
    
    def _build_analysis_prompt(self, user_data: Dict[str, Any]) -> str:
        """
        ユーザーデータをプロンプトに変換
        
        Args:
            user_data: ユーザーの集約データ
        
        Returns:
            OpenAIへ送信するプロンプト
        """
        init_answers = user_data.get("init_answers", [])
        job_history = user_data.get("job_history", {})
        
        # 初期回答をテキスト化
        answers_text = ""
        if init_answers:
            answers_text = "\n".join([
                f"【{answer.get('question_text', '')}】\nA: {answer.get('option_text', '')}"
                for answer in init_answers
            ])
        else:
            answers_text = "（初期質問への回答がありません）"
        
        # Good職業を抽出
        good_jobs = job_history.get("good_jobs", [])
        good_jobs_text = "\n".join([
            f"- {job['job_name']}"
            for job in good_jobs[:5]  # 最大5個
        ]) if good_jobs else "（Good評価がありません）"
        
        # Bad職業を抽出
        bad_jobs = job_history.get("bad_jobs", [])
        bad_jobs_text = "\n".join([
            f"- {job['job_name']}"
            for job in bad_jobs[:5]  # 最大5個
        ]) if bad_jobs else "（Bad評価がありません）"
        
        prompt = f"""
        あなたは「職業適性分析エキスパート」です。
        ユーザーの初期診断回答と職業評価履歴から、最適な職業プロファイルを生成してください。

        【初期診断回答（5問）】
{answers_text}

        【ユーザーが「Good」と評価した職業】
{good_jobs_text}

        【ユーザーが「Bad」と評価した職業】
{bad_jobs_text}

        【分析タスク】
        1. Good職業に共通する「楽しい要素」を抽出
           （例：人との関わり、創造性、データ分析など）
        2. Bad職業に共通する「つまらない要素」を抽出
           （例：単調性、孤立性、複雑性など）
        3. 初期質問から、ユーザーの思考パターン、行動特性、価値観を読み取る
        4. これらを統合し、下記フォーマットで出力

        【出力フォーマット（厳守）】
        この仕事は、[具体的な操作対象]を操作・扱い、[主な目的]を達成することに特化しています。
        具体的には、[具体的な業務内容]を行います。
        成果を出すためには、[得意なツールやスキル]を駆使し、[求める成果物]を生み出すことが求められます。
        思考タイプとしては、[ユーザーの思考の癖]が必要とされ、
        環境としては、[理想の環境]で、[対人距離感]を持って働くことが適しています。

        【重要な注意事項】
        - 実績データ（Good/Bad職業）を最優先
        - 単なる「職業名」ではなく、「その職業の中でも特定の役割」を想定すること
        - 抽象的な表現を避け、具体的な行動に置き換える
        - 出力は「この仕事は...」で始まる、一つの繋がった文章（400文字程度）のみ

        分析を開始してください。
        """
        
        return prompt
    
    def extract_job_traits_from_profile(self, profile: str) -> Dict[str, str]:
        """
        生成されたプロファイルから重要な特性を抽出
        
        Args:
            profile: AI生成されたプロファイル
        
        Returns:
            抽出された特性：
            {
                "work_object": "操作対象",
                "purpose": "目的",
                "business_content": "業務内容",
                "required_traits": "求められる特性",
                "ideal_environment": "理想の環境"
            }
        """
        # プロファイルからメインフレーズを抽出（簡易実装）
        traits = {
            "profile": profile,
            "extracted_at": "分析時刻"
        }
        return traits
