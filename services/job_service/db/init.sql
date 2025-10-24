CREATE OR REPLACE FUNCTION uuid_generate_v7() RETURNS UUID AS
$$
BEGIN
    return encode(set_bit(set_bit(overlay(
        uuid_send(gen_random_uuid())
        placing substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3)
        from 1 for 6
    ), 52, 1), 53, 1), 'hex')::uuid;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';


CREATE SCHEMA IF NOT EXISTS public;

-- industries
CREATE TABLE IF NOT EXISTS industries (
  industry_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT
);

-- job_categories
CREATE TABLE IF NOT EXISTS job_categories (
  category_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT
);

-- skills
CREATE TABLE IF NOT EXISTS skills (
  skill_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- certifications
CREATE TABLE IF NOT EXISTS certifications (
  certification_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- companies
CREATE TABLE IF NOT EXISTS companies (
  company_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- talents
CREATE TABLE IF NOT EXISTS talents (
  talent_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- interests
CREATE TABLE IF NOT EXISTS interests (
  interest_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- jobs
CREATE TABLE IF NOT EXISTS jobs (
  job_id SERIAL PRIMARY KEY,
  industry_id INTEGER NOT NULL REFERENCES industries(industry_id) ON DELETE RESTRICT,
  category_id INTEGER NOT NULL REFERENCES job_categories(category_id) ON DELETE RESTRICT,
  name TEXT NOT NULL,
  description TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_jobs_timestamp
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- job_feedbacks
CREATE TABLE IF NOT EXISTS job_feedbacks (
  feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
  salary INTEGER CHECK (salary > 0),
  level INTEGER CHECK (level > 0 AND level <= 5),
  end_time TIME,
  holiday INTEGER CHECK (holiday >= 0),
  overtime_hours INTEGER CHECK (overtime_hours >= 0),
  age INTEGER CHECK (age >= 0),
  tenure_years INTEGER CHECK (tenure_years >= 0),
  marriage_age INTEGER CHECK (marriage_age >= 0),
  gender_ratio REAL CHECK (gender_ratio >= 0),
  romance_rate REAL CHECK (romance_rate >= 0),
  social_signification TEXT,
  personality_traits TEXT,
  growth_opportunities TEXT,
  wrong_image TEXT,
  uniform BOOLEAN,
  work_life_balance REAL CHECK (work_life_balance >= 0),
  future_outlook TEXT,
  rarity REAL CHECK (rarity >= 0),
  scandal_history TEXT,
  focus_on_education BOOLEAN,
  focus_on_achievements BOOLEAN,
  appeal_points TEXT,
  daily_routine TEXT,
  comments TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_job_feedbacks_timestamp
BEFORE UPDATE ON job_feedbacks
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- feedback_skill (many-to-many: job_feedbacks <-> skills)
CREATE TABLE IF NOT EXISTS feedback_skill (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, skill_id)
);

-- feedback_certification (job_feedbacks <-> certifications)
CREATE TABLE IF NOT EXISTS feedback_certification (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  certification_id INTEGER NOT NULL REFERENCES certifications(certification_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, certification_id)
);

-- feedback_company (job_feedbacks <-> companies)
CREATE TABLE IF NOT EXISTS feedback_company (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE RESTRICT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, company_id)
);

-- feedback_talent (job_feedbacks <-> talents)
CREATE TABLE IF NOT EXISTS feedback_talent (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  talent_id INTEGER NOT NULL REFERENCES talents(talent_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, talent_id)
);

-- feedback_interest (job_feedbacks <-> interests)
CREATE TABLE IF NOT EXISTS feedback_interest (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  interest_id INTEGER NOT NULL REFERENCES interests(interest_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, interest_id)
);

-- histories (Dreamer の Job 閲覧履歴等)
CREATE TABLE IF NOT EXISTS histories (
  history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
  dreamer_id UUID NOT NULL,
  good BOOLEAN NOT NULL DEFAULT FALSE,
  bad BOOLEAN NOT NULL DEFAULT FALSE,
  save BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);