from shared.lib.API.client import Client

#job_serviceから職業データを取得する
def get_job_data(job_id: str, data_url="http://job-service:8000/api/v1/job"):
    client = Client()
    success, result, error = client.get(f"{data_url}/detail/{job_id}")
    if success:
        return result
    else:
        raise Exception(f"Job Serviceから職業データの取得に失敗しました: {error}")
"""
実行結果
{
    'job_id': 10, 
    'name': 'ローディー', 
    'description': 'ローディーとは、音楽業界で楽器や音響機材の運搬、設置、調整などを行うサポートスタッフのことです。バンドやアーティストのコンサートやツアーに同行し、ステージの準備や撤収、機材の保守管理などを担当します。', 
    'imgs': ['https://cdn.karynos.com/images/jobs/9.png'], 
    'salary': 550, 
    'level': 0, 
    'end_time': '19:30:00', 
    'holiday': 2, 
    'overtime_hours': 15, 
    'age': 32, 
    'tenure_years': 5, 
    'marriage_age': 31, 
    'gender_ratio': 85.0, 
    'romance_rate': 45.0, 
    'social_signification': '', 
    'personality_traits': '', 
    'growth_opportunities': '', 
    'wrong_image': '', 
    'uniform': False, 
    'work_life_balance': 0.0, 
    'future_outlook': '', 
    'rarity': 0.0, 
    'scandal_history': '', 
    'focus_on_education': False, 
    'focus_on_achievements': False, 
    'appeal_points': '', 
    'daily_routine': '', 
    'comments': '', 
    'skills': [
        {  
            'skill_id': 336, 
            'name': '体力と持久力', 
            'is_required': True
        }, 
        {
            'skill_id': 378, 
            'name': 'コミュニケーションスキル', 
            'is_required': True
        }, 
        {
            'skill_id': 797, 
            'name': '時間管理スキル', 
            'is_required': False
        }, 
        {
            'skill_id': 850, 
            'name': '機材の基本的な扱い方', 
            'is_required': True
        }
    ], 
    'certifications': [
        {
            'certification_id': 289, 
            'name': '運転免許', 
            'is_required': True
        }, 
        {
            'certification_id': 476, 
            'name': 'フォークリフト運転技能者', 
            'is_required': False
        }
    ], 
    'companies': [
        {
            'company_id': 431, 
            'name': '斎久工業株式会社'
        }, 
        {
            'company_id': 898, 
            'name': 'アルモント株式会社'
        }
    ], 
    'talents': [
        {
            'talent_id': 237, 
            'name': 'コミュニケーション能力', 
            'is_required': True
        }, 
        {
            'talent_id': 302, 
            'name': '継続力', 
            'is_required': True
        }, 
        {
            'talent_id': 321, 
            'name': '体力', 
            'is_required': True
        }, 
        {
            'talent_id': 358, 
            'name': '機材知識', 
            'is_required': False
        }
    ], 
    'interests': [
        {
            'interest_id': 34, 
            'name': '音楽への情熱', 
            'is_required': True
        }, 
        {
            'interest_id': 162, 
            'name': '最新技術への関心', 
            'is_required': False
        }, 
        {
            'interest_id': 363, 
            'name': '体力', 
            'is_required': True
        }
    ]
}
"""