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

/*
    Table: dreamers 
*/
CREATE TABLE dreamers (
    dreamer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id INTEGER,
    login_id TEXT NOT NULL,
    name_family TEXT NOT NULL,
    name_given TEXT NOT NULL,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_dreamer_timestamp
BEFORE UPDATE ON dreamers
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

/*
    Table: dreamer_groups 
*/
CREATE TABLE dreamer_groups (
    group_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_dreamer_group_timestamp
BEFORE UPDATE ON dreamer_groups
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

/*
    Table: dreamer_group_members  
*/
CREATE TABLE dreamer_group_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    group_id UUID NOT NULL REFERENCES dreamer_groups(group_id) ON DELETE RESTRICT,
    dreamer_id UUID NOT NULL REFERENCES dreamers(dreamer_id) ON DELETE RESTRICT,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
/*
    Table: init_questions
    初期診断用の質問マスターテーブル
*/
CREATE TABLE init_questions (
    question_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    category TEXT NOT NULL,
    question_text TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_init_questions_timestamp
BEFORE UPDATE ON init_questions
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
CREATE INDEX idx_init_questions_version_active ON init_questions(version, is_active);
CREATE INDEX idx_init_questions_category ON init_questions(category);

/*
    Table: init_question_options
    各質問の選択肢を保存
*/
CREATE TABLE init_question_options (
    option_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question_id UUID NOT NULL REFERENCES init_questions(question_id) ON DELETE CASCADE,
    option_order INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_init_question_options_question_id ON init_question_options(question_id);

/*
    Table: user_initial_answers
    ユーザーの初期診断回答を保存
*/
CREATE TABLE user_initial_answers (
    answer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    dreamer_id UUID NOT NULL REFERENCES dreamers(dreamer_id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES init_questions(question_id) ON DELETE RESTRICT,
    option_id UUID NOT NULL REFERENCES init_question_options(option_id) ON DELETE RESTRICT,
    question_version INTEGER NOT NULL,
    answered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_user_initial_answers_timestamp
BEFORE UPDATE ON user_initial_answers
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
CREATE INDEX idx_user_initial_answers_dreamer_id ON user_initial_answers(dreamer_id);
CREATE INDEX idx_user_initial_answers_question_version ON user_initial_answers(question_version);

-- =====================================================================
-- Seed Data: 初期診断質問（初期5問）バージョン1.0
-- =====================================================================

-- 質問1: 思考スタイル
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, '思考スタイル', '新しい複雑な機械やソフトを目の前にしたとき、あなたはどうしますか？', 1, TRUE);

INSERT INTO init_question_options (question_id, option_order, option_text)
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=1), 1, '説明書を最初から最後まで熟読し、構造を理解する'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=1), 2, 'とりあえず触って動かしながら、体で覚える'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=1), 3, '詳しい人に聞くか、解説動画を見る';

-- 質問2: 対人スタイル
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, '対人スタイル', '仕事をする際、理想的な周囲との関係は？', 2, TRUE);

INSERT INTO init_question_options (question_id, option_order, option_text)
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=2), 1, '家族のように仲良く、プライベートも共有したい'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=2), 2, '仕事中は協力するが、プライベートは別'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=2), 3, '完全にドライな関係で十分';

-- 質問3: 行動特性
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, '行動特性', 'じっとしているのと、動き回るの、どちらが楽？', 3, TRUE);

INSERT INTO init_question_options (question_id, option_order, option_text)
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=3), 1, 'デスクに座って一日中動かないのが一番楽'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=3), 2, '座りっぱなしは苦痛。適度に動きたい'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=3), 3, '外に出て、常に移動している方が活力が湧く';

-- 質問4: 価値観
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, '価値観', 'あなたにとって「最高の報酬」とは？', 4, TRUE);

INSERT INTO init_question_options (question_id, option_order, option_text)
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=4), 1, '給与や名誉などの外的報酬'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=4), 2, 'クライアントからの感謝や信頼'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=4), 3, '自分の作品やシステムが世に残ること';

-- 質問5: リスク志向
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, 'リスク志向', 'リスクや不確実性に対するスタンスは？', 5, TRUE);

INSERT INTO init_question_options (question_id, option_order, option_text)
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=5), 1, 'ハイリスク・ハイリターンが好き'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=5), 2, '計算できるリスクなら取る'
UNION ALL
SELECT (SELECT question_id FROM init_questions WHERE version=1 AND question_order=5), 3, '安全性・確実性が最優先';

-- ========================
-- Development Default User
-- ========================
-- デフォルト dreamer を挿入（開発用）
INSERT INTO dreamers (dreamer_id, organization_id, login_id, name_family, name_given, created_at, updated_at)
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    0,
    'dev-user',
    'Development',
    'User',
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;