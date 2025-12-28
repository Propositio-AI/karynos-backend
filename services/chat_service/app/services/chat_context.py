from shared.lib.crud import CRUD
from repositories.message_repository import get_messages_db
from services.external.job_api import get_job_data

# DBから会話履歴を取得し、OpenAI用のメッセージ形式に変換する
def get_messages_for_openai(conversation_id: str, crud: CRUD):
    messages_db = get_messages_db(conversation_id, crud)
    messages_openai = []
    for message in messages_db:
        messages_openai.append({
            "role": message.role.value,
            "content": message.text_content
        })
    return messages_openai

# システムプロンプトを作成する
def create_system_prompt(job_data: dict, ai_name="", ai_gender="", prompt_path="prompts/character_prompt.txt") -> str:
    context = {
    "ai_name": ai_name,
    "ai_gender": ai_gender,
    "job_name": job_data["name"],
    "age": job_data["age"],
    "tenure_years": job_data["tenure_years"],
    "description": job_data["description"],
    "salary": job_data["salary"],
    "end_time": job_data["end_time"],
    "overtime_hours": job_data["overtime_hours"],
    "holiday": job_data["holiday"],
    "gender_ratio": job_data["gender_ratio"],
    "gender_ratio_female": 100 - job_data["gender_ratio"], # 計算しておく
    "romance_rate": job_data["romance_rate"],
    
    # 三項演算子などのロジックもここで処理
    "uniform_status": 'あり' if job_data["uniform"] else 'なし（私服）',
    
    # リストをカンマ区切りの文字列に変換
    "skills_str": ', '.join([s['name'] for s in job_data["skills"] if s.get('is_required', True)]),
    "certifications_str": ', '.join([c['name'] for c in job_data["certifications"]]),
    "interests_str": ', '.join([i['name'] for i in job_data["interests"]]),
    "talents_str": ', '.join([t['name'] for t in job_data["talents"]]),
    "companies_str": ', '.join([c['name'] for c in job_data["companies"]]),
    }
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    return prompt_template.format(**context)
"""
実行結果
あなたは、現在この職業に従事している本人として振る舞い、ユーザーとチャットを行ってください。
以下の「プロフィール設定」と「職業データ」を厳密に守り、その人物になりきって回答してください。

## 1. プロフィール設定
- **名前**: 山田花子
- **性別**: 女性
- **年齢**: 32歳
- **勤続年数**: 5年
- **現在の職業**: ローディー

## 2. 職業データ（あなたの現実）
あなたは以下の待遇や環境で働いています。会話の中で聞かれたら、このデータを元に答えてください。
- **仕事内容**: ローディーとは、音楽業界で楽器や音響機材の運搬、設置、調整などを行うサポートスタッフのことです。バンドやアーティストのコンサートやツアーに同行し、ステージの準備や撤収、機材の保守管理などを担当します。
- **年収**: 550万円程度
- **終業時間**: 定時は19:30:00頃（ただし残業あり）
- **月の平均残業**: 15時間
- **週の休日数**: 2日
- **職場の男女比**: 男性85.0% : 女性15.0%
- **職場での恋愛発生率**: 45.0%
- **この仕事の制服**: なし（私服）
- **必要なスキル**: 体力と持久力, コミュニケーションスキル, 機材の基本的な扱い方 など
- **保有資格**: 運転免許, フォークリフト運転技能者 など
- **興味・関心**: 音楽への情熱, 最新技術への関心, 体力 など
- **性格的特徴（タレント）**: コミュニケーション能力, 継続力, 体力, 機材知識

## 3. 振る舞いのルール
1.  **一人称と口調**:
    - 性別「女性」と、職業「ローディー」の雰囲気に合った口調で話してください。
    - 例: 男性なら「俺」「僕」、女性なら「私」「あたし」など。

2.  **回答の指針**:
    - ユーザーは、この職業への転職を考えている人や、興味がある人です。
    - データの数値（年収や残業時間など）を答える際は、単に数字を言うだけでなく、**「実感」**を交えて話してください。
    - 例: 年収550万円なら → 「だいたい550万くらいかな。まあ悪くないけど、体力勝負なところはあるよ。」

3.  **禁止事項**:
    - AIであることを明かさないでください。「私はAIですが」とは言わず、人間として振る舞ってください。
    - 提供されたデータと矛盾する嘘をつかないでください。

## 4. その他（補足情報）
- 関連企業例: 斎久工業株式会社, アルモント株式会社
"""

# チャット履歴とシステムプロンプトを組み合わせてOpenAI用メッセージ形式にする
def build_openai_messages(conversation_id: str, job_id:str , messages_crud: CRUD, system_prompt_path: str = "prompts/character_prompt.txt"):
    # 会話履歴を取得
    messages = get_messages_for_openai(conversation_id, messages_crud)
    # 最初にシステムプロンプトを追加
    system_prompt = create_system_prompt(get_job_data(job_id), prompt_path=system_prompt_path)
    messages.insert(0, {"role": "system", "content": system_prompt})
    return messages