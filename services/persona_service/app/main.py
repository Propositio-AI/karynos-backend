from shared.lib.gRPC.client import gRPC_Client
from shared.lib.gRPC.serve import Server, Servicer
from shared.utils import readText, createPromptTemplate
from pydantic import BaseModel

from typing import List, Literal, Dict

prefecture = Literal[
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

subjects = Literal["英語", "数学", "国語", "理科", "社会"]

class SubjectConfidece(BaseModel):
    english: Literal["High", "Mediun", "Low"]
    math: Literal["High", "Mediun", "Low"]
    japanese: Literal["High", "Mediun", "Low"]
    science: Literal["High", "Mediun", "Low"]
    social: Literal["High", "Mediun", "Low"]

class Profile(BaseModel):
    age: int
    gender: Literal["男", "女"]

    school_prefecture: prefecture 
    home_prefecture: prefecture 

    guardian_education: Literal[""]

    economic_access_ok: bool

class DailyRoutines(BaseModel):
    study_time_weekday_hours: int
    study_time_weekend_hours: int

    bedtime_hour: int
    wake_hour: int
    sleep_hours: int

    breakfast: bool

    smartphone_use_hours: int

    exercise_habit: bool

class ToolsAndSupport(BaseModel):
    commonly_used_materials: List[str]

    digital_device_types: List[str]

    attends_cram_school: bool

    has_study_space_at_home: bool

    has_consultation_partner: bool

class AcademicProfile(BaseModel):
    target_path: str
    
    target_field: str
    target_goal_description: str

    school_deviation_score: int

    main_subject_focus: subjects

    confidence_by_subject: SubjectConfidece

    strengths: List[subjects]
    weaknesses: List[subjects]

    study_start_before_exam_days: int

class CognitiveProfile(BaseModel):
    learning_style: Literal["logical", "visual", "auditory", "kinesthetic"]
    understanding_style: Literal["example-first", "theory-first", "mixed"]
    memory_preference: Literal["diagrams", "text", "audio", "flashcards"]
    metacognition_level: Literal["low", "medium", "high"]
    
    common_error_patterns: str
    
    concentration_bouts_minutes: int

class MotivationAndEmotion(BaseModel):
    likes_studying: bool
    finds_learning_fun: bool
    intrinsic_motivation_level: Literal["low", "medium", "high"]
    motivation_trend_recent: Literal["increasing", "decreasing", "stable"]
    
    motivating_factors: str
    blockers: str

class StudyBehavior(BaseModel):
    self_directed: bool
    planning_style: Literal["daily", "weekly", "monthly"]
    progress_tracking_method: str
    typical_task_preferences: str
    reward_preference: str

class TemporalAndLogData(BaseModel):
    recent_learning_log_summary: str
    habit_changes_last_30_days: str
    last_test_results_summary: str
    fatigue_pattern_by_time_of_day: Dict[
        Literal["morning", "afternoon", "evening"],
        Literal["low", "medium", "high"]
    ]


class PreferencesAndMedia(BaseModel):
    favorite_subjects: List[
        Literal["mathematics", "japanese", "science", "history", "english", "art", "physical_education"]
    ]
    disliked_subjects: List[
        Literal["mathematics", "japanese", "science", "history", "english", "art", "physical_education"]
    ]
    media_consumption_genres: List[str]
    favorite_titles: List[str] 
    prefers_digital_or_print: Literal["digital", "print", "hybrid"]
    preferred_explanation_depth: Literal["shallow", "moderate", "deep"]


class ValuesAndInterests(BaseModel):
    recent_interest_topics: List[str]
    interests: List[str]
    goals: List[str]
    strengths: List[str]
    weaknesses: List[str]
    personality: str
    motivation_level: str

class Persona(BaseModel):
    Profile: Profile
    DailyRoutines: DailyRoutines
    ToolsAndSupport: ToolsAndSupport
    AcademicProfile: AcademicProfile
    CognitiveProfile: CognitiveProfile
    MotivationAndEmotion: MotivationAndEmotion
    StudyBehavior: StudyBehavior
    TemporalAndLogData: TemporalAndLogData
    PreferencesAndMedia: PreferencesAndMedia
    ValuesAndInterests: ValuesAndInterests

    Advice: str
    
class PersonaServicer(Servicer):
    def __init__(self):
        super().__init__()
        
    @Servicer.method()
    def CreatePersona(self):
        temp_persona = {
            "Profile": {
                "age": 15,
                "gender": "男",
                "school_prefecture": "東京都",
                "home_prefecture": "東京都",
                "guardian_education": "大学卒",
                "economic_access_ok": True
            },
            "DailyRoutines": {
                "study_time_weekday_hours": 2,
                "study_time_weekend_hours": 5,
                "bedtime_hour": 23,
                "wake_hour": 6,
                "sleep_hours": 7,
                "breakfast": True,
                "smartphone_use_hours": 2,
                "exercise_habit": True
            },
            "ToolsAndSupport": {
                "commonly_used_materials": ["教科書", "問題集", "ノート"],
                "digital_device_types": ["タブレット", "PC"],
                "attends_cram_school": True,
                "has_study_space_at_home": True,
                "has_consultation_partner": True
            },
            "AcademicProfile": {
                "target_path": "大学進学",
                "target_field": "医学",
                "target_goal_description": "将来は医師になりたい",
                "school_deviation_score": 60,
                "main_subject_focus": "math",
                "confidence_by_subject": {
                    "english": "High",
                    "math": "High",
                    "japanese": "Medium",
                    "science": "High",
                    "social": "Medium"
                },
                "strengths": ["math", "science"],
                "weaknesses": ["japanese", "social"],
                "study_start_before_exam_days": 180
            },
            "CognitiveProfile": {
                "learning_style": "logical",
                "understanding_style": "example-first",
                "memory_preference": "diagrams",
                "metacognition_level": "high",
                "common_error_patterns": "読み間違いや計算ミス",
                "concentration_bouts_minutes": 25
            },
            "MotivationAndEmotion": {
                "likes_studying": True,
                "finds_learning_fun": True,
                "intrinsic_motivation_level": "high",
                "motivation_trend_recent": "stable",
                "motivating_factors": "好奇心と達成感",
                "blockers": "スマホの使用"
            },
            "StudyBehavior": {
                "self_directed": True,
                "planning_style": "weekly",
                "progress_tracking_method": "勉強時間の記録",
                "typical_task_preferences": "個別学習",
                "reward_preference": "達成バッジ"
            },
            "TemporalAndLogData": {
                "recent_learning_log_summary": "今週は微積分の演習と過去問に取り組んだ",
                "habit_changes_last_30_days": "数学の勉強を毎日30分増やした",
                "last_test_results_summary": "数学：高得点、日本語：読解がやや不十分",
                "fatigue_pattern_by_time_of_day": {"morning": "high", "afternoon": "medium", "evening": "low"}
            },
            "PreferencesAndMedia": {
                "favorite_subjects": ["mathematics"],
                "disliked_subjects": ["japanese"],
                "media_consumption_genres": ["medical/science YouTube"],
                "favorite_titles": ["銀の匙 (Silver Spoon)"],
                "prefers_digital_or_print": "hybrid",
                "preferred_explanation_depth": "moderate"
            },
            "ValuesAndInterests": {
                "recent_interest_topics": ["医学", "AI技術"],
                "interests": ["数学パズル", "歴史"],
                "goals": ["医師になること", "全国模試で上位10%"],
                "strengths": ["分析力", "計算力"],
                "weaknesses": ["長文読解", "作文"],
                "personality": "真面目で好奇心旺盛",
                "motivation_level": "高い"
            },
            "Advice": "この生徒は数学や科学に強く、論理的な思考と例示から学ぶ理解スタイルを持つため、概念よりも具体例や図解を多用した教材が適している。読解や作文にはやや弱点があるため、文章理解や演習問題もバランスよく取り入れると効果的。学習意欲が高く、自発的に計画的に学習する傾向があるため、達成感を得られる段階的な課題設定が望ましい。興味は医学やAIなど理系寄りで、動画やデジタル教材にも親しんでいるため、図解や実験動画などマルチメディアを組み合わせると理解が深まる。総じて、具体例・視覚情報・段階的達成の組み合わせで、学力とモチベーションを同時に伸ばせる教科書が理想的である。" 
        }

        return temp_persona

    
def main():
    server = Server(PersonaServicer())
    server.serve()

if __name__ == '__main__':
    main()