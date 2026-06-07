CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION uuid_generate_v7() RETURNS UUID AS
$$
BEGIN
    RETURN encode(set_bit(set_bit(overlay(
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
$$ LANGUAGE 'plpgsql';

DO $$
BEGIN
  CREATE TYPE share_type AS ENUM ('PRIVATE', 'PUBLIC');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
  CREATE TYPE role_type AS ENUM ('user', 'assistant', 'system');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END
$$;

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS industries (
  industry_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS job_categories (
  category_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS skills (
  skill_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certifications (
  certification_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS companies (
  company_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS talents (
  talent_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interests (
  interest_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id SERIAL PRIMARY KEY,
  industry_id INTEGER NOT NULL REFERENCES industries(industry_id) ON DELETE RESTRICT,
  category_id INTEGER REFERENCES job_categories(category_id) ON DELETE RESTRICT,
  name TEXT NOT NULL,
  description TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_images (
  img_id SERIAL PRIMARY KEY,
  job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE RESTRICT,
  img_url TEXT NOT NULL,
  alt TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS feedback_skill (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, skill_id)
);

CREATE TABLE IF NOT EXISTS feedback_certification (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  certification_id INTEGER NOT NULL REFERENCES certifications(certification_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, certification_id)
);

CREATE TABLE IF NOT EXISTS feedback_company (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE RESTRICT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, company_id)
);

CREATE TABLE IF NOT EXISTS feedback_talent (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  talent_id INTEGER NOT NULL REFERENCES talents(talent_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, talent_id)
);

CREATE TABLE IF NOT EXISTS feedback_interest (
  feedback_id UUID NOT NULL REFERENCES job_feedbacks(feedback_id) ON DELETE CASCADE,
  interest_id INTEGER NOT NULL REFERENCES interests(interest_id) ON DELETE RESTRICT,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id, interest_id)
);

CREATE TABLE IF NOT EXISTS histories (
  history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
  dreamer_id UUID NOT NULL,
  good BOOLEAN NOT NULL DEFAULT FALSE,
  bad BOOLEAN NOT NULL DEFAULT FALSE,
  save BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dreamers (
  dreamer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id INTEGER,
  login_id TEXT NOT NULL,
  name_family TEXT NOT NULL,
  name_given TEXT NOT NULL,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dreamer_groups (
  group_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dreamer_group_members (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  group_id UUID NOT NULL REFERENCES dreamer_groups(group_id) ON DELETE RESTRICT,
  dreamer_id UUID NOT NULL REFERENCES dreamers(dreamer_id) ON DELETE RESTRICT,
  joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS init_questions (
  question_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  version INTEGER NOT NULL DEFAULT 1,
  category TEXT NOT NULL,
  question_text TEXT NOT NULL,
  question_order INTEGER NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS init_question_options (
  option_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  question_id UUID NOT NULL REFERENCES init_questions(question_id) ON DELETE CASCADE,
  option_order INTEGER NOT NULL,
  option_text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_initial_answers (
  answer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  dreamer_id UUID NOT NULL REFERENCES dreamers(dreamer_id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES init_questions(question_id) ON DELETE RESTRICT,
  option_id UUID NOT NULL REFERENCES init_question_options(option_id) ON DELETE RESTRICT,
  question_version INTEGER NOT NULL,
  answered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  owner_id UUID NOT NULL,
  job_id TEXT NOT NULL,
  job_name TEXT NOT NULL,
  assistant_name TEXT,
  assistant_gender TEXT,
  last_message_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  share_type share_type NOT NULL DEFAULT 'PRIVATE',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE RESTRICT,
  sender_id UUID NOT NULL,
  role role_type NOT NULL,
  text_content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation_participants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE RESTRICT,
  user_id UUID NOT NULL,
  joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_jobs_timestamp ON jobs;
CREATE TRIGGER update_jobs_timestamp
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_job_feedbacks_timestamp ON job_feedbacks;
CREATE TRIGGER update_job_feedbacks_timestamp
BEFORE UPDATE ON job_feedbacks
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_dreamer_timestamp ON dreamers;
CREATE TRIGGER update_dreamer_timestamp
BEFORE UPDATE ON dreamers
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_dreamer_group_timestamp ON dreamer_groups;
CREATE TRIGGER update_dreamer_group_timestamp
BEFORE UPDATE ON dreamer_groups
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_init_questions_timestamp ON init_questions;
CREATE TRIGGER update_init_questions_timestamp
BEFORE UPDATE ON init_questions
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_user_initial_answers_timestamp ON user_initial_answers;
CREATE TRIGGER update_user_initial_answers_timestamp
BEFORE UPDATE ON user_initial_answers
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_message_timestamp ON messages;
CREATE TRIGGER update_message_timestamp
BEFORE UPDATE ON messages
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

DROP TRIGGER IF EXISTS update_conversation_timestamp ON conversations;
CREATE TRIGGER update_conversation_timestamp
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

CREATE INDEX IF NOT EXISTS idx_init_questions_version_active ON init_questions(version, is_active);
CREATE INDEX IF NOT EXISTS idx_init_questions_category ON init_questions(category);
CREATE INDEX IF NOT EXISTS idx_init_question_options_question_id ON init_question_options(question_id);
CREATE INDEX IF NOT EXISTS idx_user_initial_answers_dreamer_id ON user_initial_answers(dreamer_id);
CREATE INDEX IF NOT EXISTS idx_user_initial_answers_question_version ON user_initial_answers(question_version);
