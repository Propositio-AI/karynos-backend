/*
    Seed Data: 初期診断質問（初期5問）
    バージョン1.0
*/

-- 質問1: 思考スタイル
INSERT INTO init_questions (version, category, question_text, question_order, is_active)
VALUES (1, '思考スタイル', '新しい複雑な機械やソフトを目の前にしたとき、あなたはどうしますか？', 1, TRUE)
RETURNING question_id INTO q1_id;

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
