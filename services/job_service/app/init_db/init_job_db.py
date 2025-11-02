from csv import DictReader

from init_db.sql_initializer import SqlInitializer

from models.CertificationTable import CertificationTable
from models.CompanyTable import CompanyTable
from models.FeedbackCertificationTable import FeedbackCertificationTable
from models.FeedbackCompanyTable import FeedbackCompanyTable
from models.FeedbackInterestTable import FeedbackInterestTable
from models.FeedbackSkillTable import FeedbackSkillTable
from models.FeedbackTalentTable import FeedbackTalentTable
from models.TalentTable import TalentTable
from models.IndustryTable import IndustryTable
from models.InterestTable import InterestTable
from models.JobCategoryTable import JobCategoryTable
from models.JobFeedbacksTabele import JobFeedbacksTable
from models.JobImageTable import JobImageTable
from models.JobsTable import JobsTable
from models.SkillTable import SkillTable
from models.TalentTable import TalentTable

certification_initializer = SqlInitializer(CertificationTable)
company_initializer = SqlInitializer(CompanyTable)
feedback_certification_initializer = SqlInitializer(FeedbackCertificationTable)
feedback_company_initializer = SqlInitializer(FeedbackCompanyTable)
feedback_interest_initializer = SqlInitializer(FeedbackInterestTable)
feedback_skill_initializer = SqlInitializer(FeedbackSkillTable)
feedback_talent_initializer = SqlInitializer(FeedbackTalentTable)
industry_initializer = SqlInitializer(IndustryTable)
interest_initializer = SqlInitializer(InterestTable)
job_category_initializer = SqlInitializer(JobCategoryTable)
job_feedbacks_initializer = SqlInitializer(JobFeedbacksTable)
job_image_initializer = SqlInitializer(JobImageTable)
jobs_initializer = SqlInitializer(JobsTable)
skill_initializer = SqlInitializer(SkillTable)
talent_initializer = SqlInitializer(TalentTable)

def parse_bool_list(value: str) -> list[bool]:
    """カンマ区切りの 'true'/'false' 文字列を bool のリストに変換"""
    # 空文字列 "" の場合は [False] になってしまうのを防ぐ
    if not value:
        return []
    return [item.strip().lower() == "true" for item in value.split(",")]

with open('.\\init_db\\職業一覧 - jobs.csv', mode='r', encoding='utf-8', newline='') as f:
    reader = DictReader(f)

    for row in reader:
        # === industries ===
        industry = industry_initializer.add_data(name=row['industry'])

        # === job_categories ===

        # === jobs ===
        job = jobs_initializer.add_data(
            industry_id=industry["industry_id"],
            name=row['職業名'],
            description=row['職業概要']   
        )

        # === job_images ===

        # === job_feedbacks ===
        job_feedback = job_feedbacks_initializer.add_data(
            job_id=job["job_id"],
            salary=row['年収'],
            holiday=row['平均休日日数'],
            overtime_hours=row['残業時間'],
            age=row['平均年齢'],
            tenure_years=row['平均滞在年'],
            marriage_age=row['結婚年齢'],
            gender_ratio=row['男性率'],
            end_time=row['平均代謝時刻']
        )

        # === skills & feedback_skills ===
        skill_names = row['スキル名'].split(",")
        is_required_skills = parse_bool_list(row['そのスキルが必須かどうか'])
        
        # zipだとリストの長さが違う場合に短い方に合わせられるため、
        # スキル名がある限りループするように修正（is_requiredはインデックスで取得）
        for i, skill_name in enumerate(skill_names):
            skill_name = skill_name.strip() # 前後の空白を削除
            if skill_name: # ★空文字列でない場合のみ処理
                skill = skill_initializer.add_data(name=skill_name)
                
                # is_required のリストがスキル名より短い場合に対応
                is_required = is_required_skills[i] if i < len(is_required_skills) else False
                
                feedback_skill = feedback_skill_initializer.add_data(
                    job_id=job[jobs_initializer.serial_col_name],
                    skill_id=skill[skill_initializer.serial_col_name],
                    is_required=is_required
                )

        
        # === certifications & feedback_certifications ===
        certification_names = row['資格名'].split(",")
        is_required_certifications = parse_bool_list(row['その資格が必須かどうか'])
        
        for i, cert_name in enumerate(certification_names):
            cert_name = cert_name.strip()
            if cert_name: # ★空文字列でない場合のみ処理
                certification = certification_initializer.add_data(name=cert_name)
                is_required = is_required_certifications[i] if i < len(is_required_certifications) else False
                
                feedback_certification = feedback_certification_initializer.add_data(
                    job_id=job[jobs_initializer.serial_col_name],
                    certification_id=certification[certification_initializer.serial_col_name],
                    is_required=is_required
                )

        # === companies & feedback_companies ===
        company_names = row['会社名'].split(",")
        for company_name in company_names:
            company_name = company_name.strip()
            if company_name: # ★空文字列でない場合のみ処理
                company = company_initializer.add_data(name=company_name)
                feedback_company = feedback_company_initializer.add_data(
                    job_id=job[jobs_initializer.serial_col_name],
                    company_id=company[company_initializer.serial_col_name]
                )

        # === talents & feedback_talents ===
        talent_names = row['才能名'].split(",")
        is_required_talents = parse_bool_list(row['その才能が必須かどうか'])
        
        for i, talent_name in enumerate(talent_names):
            talent_name = talent_name.strip()
            if talent_name: # ★空文字列でない場合のみ処理
                talent = talent_initializer.add_data(name=talent_name)
                is_required = is_required_talents[i] if i < len(is_required_talents) else False

                feedback_talent = feedback_talent_initializer.add_data(
                    job_id=job[jobs_initializer.serial_col_name],
                    talent_id=talent[talent_initializer.serial_col_name],
                    is_required=is_required
                )

        # === interests & feedback_interests ===
        interest_names = row['興味・関心'].split(",")
        is_required_interests = parse_bool_list(row['その興味・関心が必須かどうか'])
        
        for i, interest_name in enumerate(interest_names):
            interest_name = interest_name.strip()
            if interest_name: # ★空文字列でない場合のみ処理
                interest = interest_initializer.add_data(name=interest_name)
                is_required = is_required_interests[i] if i < len(is_required_interests) else False

                feedback_interest = feedback_interest_initializer.add_data(
                    job_id=job[jobs_initializer.serial_col_name],
                    interest_id=interest[interest_initializer.serial_col_name],
                    is_required=is_required
                )

export_dir = ".\\..\\db\\"
certification_initializer.export_to_sql(export_dir)
company_initializer.export_to_sql(export_dir)
feedback_certification_initializer.export_to_sql(export_dir)
feedback_company_initializer.export_to_sql(export_dir)
feedback_interest_initializer.export_to_sql(export_dir)
feedback_skill_initializer.export_to_sql(export_dir)
feedback_talent_initializer.export_to_sql(export_dir)
talent_initializer.export_to_sql(export_dir)
industry_initializer.export_to_sql(export_dir)
interest_initializer.export_to_sql(export_dir)
job_category_initializer.export_to_sql(export_dir)
job_feedbacks_initializer.export_to_sql(export_dir)
job_image_initializer.export_to_sql(export_dir)
jobs_initializer.export_to_sql(export_dir)
skill_initializer.export_to_sql(export_dir)
talent_initializer.export_to_sql(export_dir)